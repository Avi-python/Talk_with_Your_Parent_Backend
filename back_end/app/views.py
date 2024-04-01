from django.shortcuts import render
from django.http import JsonResponse, response
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()
client = OpenAI()

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

# @permission_classes([IsAuthenticated])
@api_view(['POST'])
def openai(request):       
    # messages = json.load(open('./assets/messages.json', 'r'))
    param = request.data['params']

    messages = param["messages"]

    openai.api_key = os.getenv("OPENAI_API_KEY")

    # messages.append({"role": "user", "content": input})
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
    )

    chunks = []
    for choice in response.choices:
        chunks.append(choice.message.content)
    single_object = "".join(chunks)

    return JsonResponse({"content": single_object});

    # 這邊應該要處理一下
    # time.sleep(1)
    # messages.append({"role": "assistant", "content": single_object})

