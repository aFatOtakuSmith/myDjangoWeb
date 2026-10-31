import os
import django
import paho.mqtt.client as mqtt
import json

# 1. 初始化 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mydearweb.settings')
django.setup()

from iot.models import DeviceData

# 2. MQTT 连接成功回调
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ 成功连接到 MQTT Broker")
        # 订阅单片机发数据的主题（+ 代表任意设备ID）
        client.subscribe("myhome/device/+/data")
        print("📡 已订阅主题: myhome/device/+/data")
    else:
        print(f"❌ 连接失败，错误码: {rc}")

# 3. 接收消息回调（核心容错逻辑）
def on_message(client, userdata, msg):
    try:
        # 将原始字节解码为字符串
        raw_str = msg.payload.decode('utf-8')
        
        # 🌟 核心容错：只提取从第一个 "{" 到最后一个 "}" 之间的内容
        start_idx = raw_str.find('{')
        end_idx = raw_str.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            clean_json_str = raw_str[start_idx:end_idx+1]
        else:
            clean_json_str = raw_str.strip() # 如果没有花括号，就只去除首尾空格
            
        # 解析 JSON
        payload = json.loads(clean_json_str)
        
        # 提取设备 ID（优先从 Topic 提取，如果没有则从 JSON 里的 device_id 提取）
        topic_parts = msg.topic.split('/')
        device_id = topic_parts[2] if len(topic_parts) >= 4 else payload.get("device_id", "unknown")

        # 存入数据库
        data = DeviceData.objects.create(
            device_id=device_id,
            payload=payload
        )
        print(f"💾 数据已入库 [{device_id}]: {payload}")
        
    except Exception as e:
        print(f"⚠️ 数据解析或保存失败: {e}")
        print(f"❌ 原始报文内容: {msg.payload}") # 打印原始内容，方便以后排查

# 4. 配置并启动 MQTT 客户端
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# 🌟 必须加上用户名和密码验证，否则会被服务器拒绝
client.username_pw_set("testclient", "20041106A")

# 连接服务器
client.connect("127.0.0.1", 1883, 60)

print("🚀 监听脚本已启动，等待设备发来数据...")
client.loop_forever()