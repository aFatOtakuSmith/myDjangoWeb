from django.urls import path
from . import views

app_name = 'ai_chat'

urlpatterns = [
    path('', views.agent_list, name='agent_list'),
    path('create/', views.create_agent, name='create_agent'),
    path('chat/<int:agent_id>/', views.chat_room, name='chat_room'),
    path('send/', views.send_message, name='send_message'),
    path('edit/<int:agent_id>/', views.edit_agent, name='edit_agent'),
    path('delete/<int:agent_id>/', views.delete_agent, name='delete_agent'),
    path('clear/<int:agent_id>/', views.clear_chat, name='clear_chat'), # 🌟 新增
]