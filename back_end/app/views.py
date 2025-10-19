from django.shortcuts import render
from django.http import JsonResponse, response, StreamingHttpResponse, HttpResponse
from django.conf import settings
from authentication.serializers import UserSerializer 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Personality

from .VC_inference import load_vc_model, vc_fn
from .ai import load_chat_model, send_messages, detect_chinese_punctuation, clear_conversation_memory

import os
import time
import tiktoken
import base64

maximum_tokens = int(os.getenv("MAXIMUM_CONVERSATION_TOKENS", 500))
encoding = tiktoken.get_encoding("cl100k_base") # for gpt-3.5-turbo and gpt-4
users_conversation_tokens = {}

# Create your views here.
# 在前面裝一個 decorator，可以檢查請求是否含有 access token。

# 維護一個全域變數，用來記錄目前使用者對應已經使用的 tokens 數量。

@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def function1(request):
    param1 = request.GET.get('param1', '沒有這個參數') # 'not found' 是 dafult value
    print(param1)
    response = {}
    response['Access-Control-Allow-Origin'] = 'http://localhost:8000'
    response['msg'] = 'hello world'
    # vc_fn(param1)
    return JsonResponse(response);

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def openai(request):       
    # messages = json.load(open('./assets/messages.json', 'r'))

    serializer = UserSerializer(request.user)

    param = request.data['params']
    messages = param["messages"]
    model_name = param["personality_name"]

    print("openai_model_name: ", model_name)

    if(users_conversation_tokens.get(serializer.data["id"]) == None):
        users_conversation_tokens[serializer.data["id"]] = 0
    users_conversation_tokens[serializer.data["id"]] += len(encoding.encode(messages))

    def event_stream():
            all_chunks = ""
            chunk = ""
            mark = 0
            for line in send_messages(messages=messages, userId=serializer.data["id"]):
                text = line
                if(text == None or len(text) == 0):
                     continue
                if(detect_chinese_punctuation(text)):
                     vc_fn(chunk.replace("\n", "").replace(" ", ""), mark, model_name) 
                     mark += 1
                     print("DEBUG: text: ", chunk + text)
                     yield (chunk + text)
                     chunk = ""
                     continue
                chunk += text
                all_chunks += text
            users_conversation_tokens[serializer.data["id"]] += len(encoding.encode(all_chunks))
            print("DEBUG: user: ", serializer.data["id"], "already use", users_conversation_tokens[serializer.data["id"]], "tokens")
            

    response = StreamingHttpResponse(event_stream(), content_type='text/plain')
    response['Cache-Control']= 'no-cache',
    response['Access-Control-Allow-Origin'] = '*',

    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_tokens(request):
    serializer = UserSerializer(request.user)
    return JsonResponse({"tokens": users_conversation_tokens[serializer.data["id"]], "isFull" : users_conversation_tokens[serializer.data["id"]] > maximum_tokens}, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reset_conversation_tokens(request):
    serializer = UserSerializer(request.user)
    clear_conversation_memory(serializer.data["id"])
    users_conversation_tokens[serializer.data["id"]] = 0
    return JsonResponse({"msg": "reset conversation tokens success"}, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audio_file(request):
    mark = request.GET.get('mark', '_init')
    model_name = request.GET.get('personality_name', "柯文哲")

    print("audio_file_model_name: ", model_name)
    
    filename = f'{model_name}{str(mark)}'
    filepath = f'D:\\College_things\\College_Program\\Backend\\audio_files\\{filename}.wav'
    print("DEBUG: filepath: ", filepath)
    times = 0
    while not os.path.exists(filepath) and times < 5: # TODO 測試這個等待到底有沒有用
        time.sleep(1)
        times += 1
        print("DEBUG: wait for audio file, times: ", times)
    
    if(times == 5):
        return JsonResponse({"msg": "audio file not found"}, status=404)
    
    with open(filepath, 'rb') as file:
        response = HttpResponse(file.read(), content_type='audio/wav') # 使用 HttpResponse 來回傳檔案，不用 FileResponse
        response['Content-Disposition'] = f'attachment; filename="{filename}.wav"'
    
    return response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_personalities(request):
    print(request.data)

    personalities = Personality.objects.all();

    result = []

    for personality in personalities:
        # print("personality: ", personality.image.path)
        with open(personality.image.path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

        result.append({
            "name": personality.name,
            "description": personality.description,
            "image": encoded_string
        })

    # print("personalities: ", personalities)

    return JsonResponse({"personalities": result}, status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def load_model(request):
    model_name = request.data["personality_name"]

    target = Personality.objects.get(name=model_name)

    load_chat_model(target.description)
    load_vc_model(model_name)

    return JsonResponse({"msg": "load model success"}, status=200)



