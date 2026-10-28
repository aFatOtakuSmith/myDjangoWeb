from django.shortcuts import render, get_object_or_404
from .models import Work
import markdown

def works_list(request):
    featured_work = Work.objects.filter(is_featured=True).first()
    works = Work.objects.all()
    return render(request, 'works/works_list.html', {
        'featured_work': featured_work,
        'works': works
    })

def work_detail(request, pk):
    work = get_object_or_404(Work, pk=pk)
    
    if work.description:
        work.description_html = markdown.markdown(
            work.description, 
            extensions=[
                'extra',                 
                'pymdownx.tasklist',     
                'pymdownx.arithmatex',   # 🌟 必须加回这个，防止公式被转义
            ],
            extension_configs={
                'pymdownx.tasklist': {
                    'custom_checkbox': True,
                },
                'pymdownx.arithmatex': {
                    'generic': True,     # 🌟 关键：输出标准包裹格式
                }
            }
        )
    else:
        work.description_html = ""
        
    return render(request, 'works/work_detail.html', {'work': work})