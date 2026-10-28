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
    # 获取所有的分类
    categories = QuoteCategory.objects.all()
    
    current_type_id = request.GET.get('type')
    # 如果没传参，自动取第一个分类
    if not current_type_id and categories.exists():
        current_type_id = str(categories.first().id)

    quotes = []
    if current_type_id:
        try:
            # 获取对应分类下的所有句子
            category = QuoteCategory.objects.get(id=current_type_id)
            quotes = category.quotes.all()
        except QuoteCategory.DoesNotExist:
            pass

    return render(request, 'core/quotes.html', {
        'categories': categories,
        'quotes': quotes,
        'current_type_id': current_type_id
    })