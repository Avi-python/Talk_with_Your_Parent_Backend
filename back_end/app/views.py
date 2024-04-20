from django.shortcuts import render
from django.http import JsonResponse, response, StreamingHttpResponse, HttpResponse
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .VC_inference import vc_fn
from .ai import send_messages, detect_chinese_punctuation

import os
import time

# Create your views here.
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

    print("debug: ", request.data)

    param = request.data['params']
    messages = param["messages"]

    def event_stream():
            chunks = ""
            mark = 0
            for line in send_messages(messages=messages):
                text = line
                if(text == None or len(text) == 0):
                     continue
                if(detect_chinese_punctuation(text)):
                     vc_fn(chunks.replace("\n", "").replace(" ", ""), mark)
                     mark += 1
                     print("DEBUG: text: ", chunks + text)
                     yield (chunks + text)
                     chunks = ""
                     continue
                chunks += text

    response = StreamingHttpResponse(event_stream(), content_type='text/plain')
    response['Cache-Control']= 'no-cache',
    response['Access-Control-Allow-Origin'] = '*',

    return response

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

