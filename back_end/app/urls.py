from django.urls import path
from . import views

urlpatterns = [
    path('function1/', views.function1),  
    path('openai/', views.openai), 
    path('audio_file/', views.audio_file),
    path('conversation_tokens/', views.conversation_tokens),
    path('reset_conversation_tokens/', views.reset_conversation_tokens),
]