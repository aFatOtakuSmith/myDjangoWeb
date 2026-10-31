from django.urls import path
from . import views

app_name = 'iot'

urlpatterns = [
    # 你之前的监控面板
    path('', views.dashboard, name='dashboard'),
    
    # 🌟 下发控制指令的 API（确保这一行真的存在！）
    # 注意结尾必须有斜杠，参数按 / 分隔
    path('api/control/<str:device_id>/<str:field>/<str:value>/', views.control_device, name='control_device'),
]