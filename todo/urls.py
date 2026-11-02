from django.urls import path
from . import views

app_name = 'todo'  # 🌟 确保有这行

urlpatterns = [
    path('', views.todo_list, name='todo_list'),
    path('add/', views.todo_add, name='todo_add'),
    path('edit/<int:pk>/', views.todo_edit, name='todo_edit'), # 🌟 新增
]