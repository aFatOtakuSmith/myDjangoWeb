from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import BlogPost
import markdown

def blog_list(request):
    posts_list = BlogPost.objects.filter(is_public=True)
    
    # 🌟 搜索逻辑：只针对标题和标签
    q = request.GET.get('q')
    if q:
        posts_list = posts_list.filter(
            Q(title__icontains=q) | 
            Q(tags__icontains=q)   # 只保留这两个
        )
    
    # 分页
    paginator = Paginator(posts_list, 8)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    # 获取所有标签供左侧展示
    all_tags = set()
    for post in BlogPost.objects.filter(is_public=True):
        for tag in post.tag_list:
            all_tags.add(tag)

    return render(request, 'blog/blog_list.html', {
        'posts': page_obj,
        'page_obj': page_obj,
        'q': q,
        'all_tags': list(all_tags)
    })

def blog_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk, is_public=True)
    
    # 将 Markdown 转换为 HTML（带数学公式和任务列表支持）
    if post.content:
        post.content_html = markdown.markdown(
            post.content, 
            extensions=['extra', 'pymdownx.tasklist', 'pymdownx.arithmatex'],
            extension_configs={
                'pymdownx.tasklist': {'custom_checkbox': True},
                'pymdownx.arithmatex': {'generic': True}
            }
        )
    else:
        post.content_html = ""
        
    return render(request, 'blog/blog_detail.html', {'post': post})