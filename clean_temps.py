import os
import time
import django

# =========================================
# 🌟 核心修复：手动加载 Django 环境
# =========================================
# 这里的 'mydearweb.settings' 需要换成你实际的 settings.py 所在的模块路径
# 如果你的项目文件夹叫 mydearweb，那就不需要改。
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mydearweb.settings')
django.setup()
# =========================================

from django.conf import settings

def clean_temp_folder():
    temp_dir = os.path.join(settings.MEDIA_ROOT, 'temps')
    if not os.path.exists(temp_dir):
        print(f"文件夹 {temp_dir} 不存在，无需清理。")
        return
    
    now = time.time()
    count = 0
    # 遍历 temps 文件夹
    for filename in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, filename)
        # 如果文件是文件，且最后修改时间超过了 24 小时（86400秒）
        if os.path.isfile(file_path) and os.stat(file_path).st_mtime < now - 86400:
            try:
                os.remove(file_path)
                print(f"已清理废弃临时图片: {filename}")
                count += 1
            except Exception as e:
                print(f"清理失败: {e}")
                
    if count == 0:
        print("没有发现超过 24 小时的废弃临时图片。")

if __name__ == '__main__':
    clean_temp_folder()