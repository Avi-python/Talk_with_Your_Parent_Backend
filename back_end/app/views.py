from django.shortcuts import render
from django.http import JsonResponse, response, StreamingHttpResponse
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from dotenv import load_dotenv
from openai import OpenAI
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
    param1 = request.GET.get('param1', 'not found') # 'not found' 是 dafult value
    print(param1)
    response = {}
    response['Access-Control-Allow-Origin'] = 'http://localhost:8000'
    response['msg'] = 'hello world'
    return JsonResponse(response);

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def openai(request):       
    # messages = json.load(open('./assets/messages.json', 'r'))

    print("debug: ", request.data)

    param = request.data['params']
    messages = param["messages"]

    def event_stream():
            for line in send_messages(messages=messages):
                text = line.choices[0].delta.content
                print(text)
                if text != None and len(text): 
                    yield text

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