from django.shortcuts import render
from django.http import HttpResponse

# 列表页视图
def blog_list(request):
    # 这里以后会从数据库读取文章列表，现在先返回一个测试文本
    return HttpResponse("这是博客的列表页")
