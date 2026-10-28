from django.urls import path
from . import views

app_name = 'works'

urlpatterns = [
    path('', views.works_list, name='works_list'),
    # 🌟 新增：例如 /works/1/ 
    path('<int:pk>/', views.work_detail, name='work_detail'),
]