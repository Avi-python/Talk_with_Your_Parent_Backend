from django.shortcuts import render
from django.http import JsonResponse, response, StreamingHttpResponse, HttpResponse
from django.conf import settings
from authentication.serializers import UserSerializer 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .VC_inference import vc_fn
from .ai import send_messages, detect_chinese_punctuation, clear_conversation_memory

import os
import time
import tiktoken
import threading

lock = threading.Lock()

maximum_tokens = int(os.getenv("MAXIMUM_CONVERSATION_TOKENS", 500))
maximum_connection = int(os.getenv("MAXIMUM_CONNECTION", 1))
maximum_idle_time = int(os.getenv("MAXIMUM_CONNECTED_TIME", 30))
encoding = tiktoken.get_encoding("cl100k_base") # for gpt-3.5-turbo and gpt-4

# 維護一個全域變數，用來記錄目前使用者對應已經使用的 tokens 數量。
users_conversation_tokens = {}
# 維護一個全域變數，用來紀錄目前使用者多久沒有進入對話。
users_conversation_timer = {}
# 維護一個 waiting queue，記錄誰先排隊的
users_waiting_queue = []

# 在前面裝一個 decorator，可以檢查請求是否含有 access token。
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

    if(users_conversation_tokens.get(serializer.data["id"]) == None):
        return JsonResponse({"msg": "It's not your turn !"}, status=403)
    
    with lock:
        users_conversation_timer[serializer.data["id"]].cancel()
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
                     vc_fn(chunk.replace("\n", "").replace(" ", ""), mark) 
                     mark += 1
                     print("DEBUG: text: ", chunk + text)
                     yield (chunk + text)
                     chunk = ""
                     continue
                chunk += text
                all_chunks += text
            with lock:
                users_conversation_tokens[serializer.data["id"]] += len(encoding.encode(all_chunks))
                print("DEBUG: user: ", serializer.data["id"], "already use", users_conversation_tokens[serializer.data["id"]], "tokens")
                create_Timer(serializer.data["id"])
            

    response = StreamingHttpResponse(event_stream(), content_type='text/plain')
    response['Cache-Control']= 'no-cache',
    response['Access-Control-Allow-Origin'] = '*',

    return response

def create_Timer(userId):
    users_conversation_timer[userId] = threading.Timer(maximum_idle_time, kick_out_user, args=[userId])
    users_conversation_timer[userId].start()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_tokens(request):
    serializer = UserSerializer(request.user)
    return JsonResponse({"tokens": users_conversation_tokens[serializer.data["id"]], "isFull" : users_conversation_tokens[serializer.data["id"]] > maximum_tokens}, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reset_conversation_tokens(request):
    serializer = UserSerializer(request.user)
    with lock:
        clear_conversation_memory(serializer.data["id"])
        users_conversation_tokens[serializer.data["id"]] = 0
    return JsonResponse({"msg": "reset conversation tokens success"}, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wait_or_access(request):
    serializer = UserSerializer(request.user)
    with lock:
        print("DEBUG: users_conversation_tokens length ", users_conversation_tokens)
        print("DEBUG: users_waiting_queue ", users_waiting_queue)
        if(users_conversation_tokens.get(serializer.data["id"]) == None):
            if(len(users_conversation_tokens) < maximum_connection and (len(users_waiting_queue) == 0 or (users_waiting_queue[0] == serializer.data["id"]))):
                # 幫使用者分配 tokens 以及設定 timer
                    users_conversation_tokens[serializer.data["id"]] = 0
                    create_Timer(serializer.data["id"])
                    if(len(users_waiting_queue) > 0):
                        users_waiting_queue.pop(0) # 第一個就是它
                    return JsonResponse({"wait": False}, status=200)
            else:
                if((serializer.data["id"] not in users_waiting_queue)):
                    users_waiting_queue.append(serializer.data["id"])
                return JsonResponse({"wait": True}, status=200)
                
                # 操作等待佇列之類的       
        else:
            return JsonResponse({
                "wait": True,
                "msg" : "You already inside the chatting page",
                }, status=403)

def kick_out_user(userId):
    print("kick out user: ", userId)
    clear_conversation_memory(userId)
    users_conversation_tokens.pop(userId)
    users_conversation_timer.pop(userId)
    print("after kick out")
    print("users_conversation_tokens: ", users_conversation_tokens)
    print("users_conversation_timer: ", users_conversation_timer)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def audio_file(request):
    mark = request.GET.get('mark', '_init')
    filename = f'ppp{str(mark)}'
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

