from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator  # 🌟 必须加上这一行，否则会报 NameError
from .models import Work, WorkCategory
import markdown

def works_list(request):
    categories = WorkCategory.objects.all()
    current_cat_id = request.GET.get('cat', 'all')

    # 🌟 把内部变量名改为了 queryset，防止和函数名 works_list 冲突
    if current_cat_id == 'all' or not current_cat_id:
        queryset = Work.objects.all()
        featured_work = queryset.filter(is_featured=True).first()
    else:
        queryset = Work.objects.filter(category_id=current_cat_id)
        featured_work = queryset.filter(is_featured=True).first()

    # 每页展示 9 个
    paginator = Paginator(queryset, 9) 
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'works/works_list.html', {
        'categories': categories,
        'current_cat_id': current_cat_id,
        'featured_work': featured_work,
        'works': page_obj,
        'page_obj': page_obj
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