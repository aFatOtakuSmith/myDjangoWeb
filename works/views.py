from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Work, WorkCategory
import markdown

def works_list(request):
    # 🌟 分类按 order 排序
    categories = WorkCategory.objects.all().order_by('order')
    
    current_cat_id = request.GET.get('cat', 'all')
    q = request.GET.get('q', '')

    if current_cat_id == 'all' or not current_cat_id:
        # 🌟 作品按 order 和时间排序
        queryset = Work.objects.all().order_by('order', '-created_at')
    else:
        queryset = Work.objects.filter(category_id=current_cat_id).order_by('order', '-created_at')
        
    if q:
        queryset = queryset.filter(Q(title__icontains=q) | Q(summary__icontains=q))
        featured_work = None 
    else:
        featured_work = queryset.filter(is_featured=True).first()

    paginator = Paginator(queryset, 9) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'works/works_list.html', {
        'categories': categories,
        'current_cat_id': current_cat_id,
        'featured_work': featured_work,
        'works': page_obj,
        'page_obj': page_obj,
        'q': q,
    })

def work_detail(request, pk):
    work = get_object_or_404(Work, pk=pk)
    if work.description:
        work.description_html = markdown.markdown(
            work.description, 
            extensions=['extra', 'pymdownx.tasklist', 'pymdownx.arithmatex'],
            extension_configs={
                'pymdownx.tasklist': {'custom_checkbox': True},
                'pymdownx.arithmatex': {'generic': True}
            }
        )
    else:
        work.description_html = ""
    return render(request, 'works/work_detail.html', {'work': work})