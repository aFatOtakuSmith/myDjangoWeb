from django.shortcuts import render
# 🌟 修复：把 QuoteFile 改成 QuoteCategory
from .models import QuoteCategory  

def index(request):
    return render(request, 'core/index.html')

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    return render(request, 'core/contact.html')

def quotes_list(request):
    categories = QuoteCategory.objects.all()
    
    # 获取 URL 里的 type 参数 (比如 'sentence_1')
    current_type_str = request.GET.get('type', '')
    
    # 如果没传参数，默认选中第一个分类，并拼上 sentence_ 前缀
    if not current_type_str and categories.exists():
        current_type_str = f"sentence_{categories.first().id}"

    # 🌟 核心修复：把 "sentence_" 替换成空，提取出真实的数字 ID
    real_id = current_type_str.replace('sentence_', '')
    
    quotes = []
    if real_id:
        try:
            # 用提取出的纯数字 ID 去查询数据库
            category = QuoteCategory.objects.get(id=real_id)
            quotes = category.quotes.all()
        except (QuoteCategory.DoesNotExist, ValueError):
            pass

    return render(request, 'core/quotes.html', {
        'categories': categories,
        'quotes': quotes,
        'current_type_id': current_type_str  # 传给前端用于高亮
    })