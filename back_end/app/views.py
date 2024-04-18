from django.shortcuts import render
from django.http import JsonResponse, response, StreamingHttpResponse
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from dotenv import load_dotenv
from openai import OpenAI

from .VC_inference import vc_fn
import re

import os
import time

load_dotenv()
client = OpenAI()

OpenAI.api_key = os.getenv("OPENAI_API_KEY")

# Create your views here.
# 在前面裝一個 decorator，可以檢查請求是否含有 access token。

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def function1(request):
    param1 = request.GET.get('param1', '沒有這個參數') # 'not found' 是 dafult value
    print(param1)
    response = {}
    response['Access-Control-Allow-Origin'] = 'http://localhost:8000'
    response['msg'] = 'hello world'
    # vc_fn(param1)
    return JsonResponse(response);

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def openai(request):       
    # messages = json.load(open('./assets/messages.json', 'r'))

    print("debug: ", request.data)

    param = request.data['params']
    messages = param["messages"]

    def event_stream():
            chunks = ""
            mark = 0
            for line in send_messages(messages=messages):
                text = line.choices[0].delta.content
                print("text: ", text)
                if(text == None or len(text) == 0):
                     continue
                if(detect_chinese_punctuation(text)):
                     vc_fn(chunks, mark)
                     mark += 1
                     yield chunks + text
                     chunks = ""
                chunks += text
                # if text != None and len(text): 
                #     yield text

    response = StreamingHttpResponse(event_stream(), content_type='text/plain')
    response['Cache-Control']= 'no-cache',
    response['Access-Control-Allow-Origin'] = '*',

    return response

def send_messages(messages):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": messages
            }
        ],
        temperature=1,
        max_tokens=725,
        top_p=0.7,
        frequency_penalty=2,
        presence_penalty=1,
        stream=True
    )

    return response

def detect_chinese_punctuation(text):
    """
    Detects Chinese punctuation marks in the given text.

    Args:
    - text (str): The input text to search for Chinese punctuation marks.

    Returns:
    - list: A list of Chinese punctuation marks found in the text.
    """
    # Regular expression pattern for Chinese punctuation marks
    # chinese_punctuation_pattern = r'[，。、；：？！“”‘’（）【】《》「」『』【】〔〕﹁﹂〈〉《》〖〗…—～·﹏]'
    chinese_punctuation_pattern = r'[，。、；：？！]'
    
    # Find all occurrences of Chinese punctuation marks in the text
    chinese_punctuation_marks = re.findall(chinese_punctuation_pattern, text)
    
    return chinese_punctuation_marks