from django.urls import path
from . import views

app_name = 'novel'

urlpatterns = [
    path('', views.novel_list, name='novel_list'),
    path('<int:pk>/', views.novel_detail, name='novel_detail'),
    path('chapter/<int:pk>/', views.chapter_read, name='chapter_read'), # 🌟 新增
]