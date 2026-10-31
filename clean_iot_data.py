import os
import django
from datetime import timedelta

# 1. 初始化 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mydearweb.settings')
django.setup()

from django.utils import timezone
from iot.models import DeviceData

def clean_old_data():
    # 2. 计算 72 小时前的时间节点
    cutoff_time = timezone.now() - timedelta(hours=72)
    
    # 3. 查找并删除旧数据
    old_records = DeviceData.objects.filter(created_at__lt=cutoff_time)
    count = old_records.count()
    
    if count > 0:
        old_records.delete()
        print(f"🧹 清理成功：删除了 {count} 条 72 小时前的旧数据。")
    else:
        print("✨ 数据库很干净，没有需要清理的旧数据。")

if __name__ == '__main__':
    clean_old_data()