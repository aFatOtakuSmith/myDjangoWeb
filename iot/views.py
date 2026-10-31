from django.shortcuts import render
from .models import DeviceData
import paho.mqtt.publish as publish
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

def dashboard(request):
    # 获取最新 50 条数据
    records = DeviceData.objects.all()[:50]
    return render(request, 'iot/dashboard.html', {'records': records})

@csrf_exempt # 测试阶段免除 CSRF 验证，方便外部请求
def control_device(request, device_id, field, value):
    """
    接收网页下发指令的 API
    例如：/api/control/STM32F103_Node01/light/1/
    """
    if request.method == 'POST':
        try:
            # 1. 使用 json.dumps 构建安全的 JSON 格式，防止特殊字符破坏结构
            payload_dict = {field: value}
            payload = json.dumps(payload_dict)
            
            # 2. 拼接下发主题
            topic = f"myhome/device/{device_id}/cmd"
            
            # 3. 打印日志，方便你在 Django 终端查看是否真的触发了下发
            print(f"📤 收到前端请求，准备下发 -> Topic: {topic}, Payload: {payload}")
            
            # 4. 调用 paho-mqtt 发送数据给服务器本地的 Mosquitto
            publish.single(
                topic=topic,
                payload=payload,
                hostname="127.0.0.1", # 服务器本机
                port=1883,
                auth={'username': "testclient", 'password': "20041106A"} # 必须使用高权限账号
            )
            
            # 5. 返回成功信息给网页
            return JsonResponse({"status": "success", "msg": f"成功下发指令: {payload}"})
            
        except Exception as e:
            # 打印详细报错到终端
            print(f"❌ 下发失败: {str(e)}")
            return JsonResponse({"status": "error", "msg": str(e)}, status=500)
            
    return JsonResponse({"status": "error", "msg": "只支持 POST 请求"}, status=405)