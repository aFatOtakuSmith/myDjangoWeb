# 导入 Django 的路由函数和视图模块
from django.urls import path
from . import views  # 导入当前 app 下的 views.py 文件

app_name='blog'
# urlpatterns 是一个列表，Django 会从上到下依次匹配 URL
urlpatterns = [
    # 首页/列表页：访问 http://127.0.0.1:8000/blog/ 时触发
    # 对应 views.py 中的 blog_list 函数，命名为 'blog_list'
    path('', views.blog_list, name='blog_list'),
]