from django.shortcuts import render
from django.http import JsonResponse, response
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

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