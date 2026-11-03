#!/bin/bash
echo "1. 收集静态文件..."
/home/aFatOtaku/newTravel/venv/bin/python manage.py collectstatic --noinput

echo "2. 执行数据库迁移..."
/home/aFatOtaku/newTravel/venv/bin/python manage.py migrate

echo "3. 重启 Gunicorn..."
sudo systemctl restart gunicorn

echo "✅ 更新完成！"
