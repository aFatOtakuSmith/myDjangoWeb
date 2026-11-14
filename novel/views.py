from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from urllib.parse import quote
import json

from .models import Novel, Volume, Chapter, Setting

# ==========================================
# 1. 我的作品库（作家控制台）
# ==========================================
@login_required
def novel_list(request):
    novels = Novel.objects.filter(user=request.user)
    return render(request, 'novel/dashboard.html', {'novels': novels})

# ==========================================
# 2. 创建新书（完成后返回作品库）
# ==========================================
@login_required
def create_novel(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        summary = request.POST.get('summary', '')
        if title:
            novel = Novel.objects.create(user=request.user, title=title, summary=summary)
            volume = Volume.objects.create(novel=novel, title='第一卷', sort_order=1)
            Chapter.objects.create(volume=volume, title='第一章', sort_order=1)
            
            # 🌟 创建后返回作品库
            return redirect('novel:novel_list')
    return render(request, 'novel/create_novel.html')

# ==========================================
# 3. 修改书籍信息
# ==========================================
@login_required
def edit_novel(request, novel_id):
    novel = get_object_or_404(Novel, id=novel_id, user=request.user)
    if request.method == 'POST':
        novel.title = request.POST.get('title', novel.title)
        novel.summary = request.POST.get('summary', novel.summary)
        if request.FILES.get('cover'):
            novel.cover = request.FILES.get('cover')
        novel.save()
        return redirect('novel:novel_list')
    return redirect('novel:novel_list')

# ==========================================
# 4. 删除整本书
# ==========================================
@login_required
@require_POST
def delete_novel(request, novel_id):
    novel = get_object_or_404(Novel, id=novel_id, user=request.user)
    novel.delete()
    return JsonResponse({'status': 'success'})

# ==========================================
# 5. 沉浸式写作台
# ==========================================
@login_required
def write_book(request, novel_id):
    novel = get_object_or_404(Novel, id=novel_id, user=request.user)
    volumes = novel.volumes.all().prefetch_related('chapters')
    return render(request, 'novel/writer.html', {
        'novel': novel,
        'volumes': volumes
    })

# ==========================================
# 6. 一键导出 TXT
# ==========================================
@login_required
def export_txt(request, novel_id):
    novel = get_object_or_404(Novel, id=novel_id, user=request.user)
    response = HttpResponse(content_type='text/plain; charset=utf-8')
    filename = quote(f"{novel.title}.txt")
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    content = f"书名：{novel.title}\n"
    content += f"作者：{novel.user.username}\n"
    content += f"简介：\n{novel.summary}\n\n"
    content += "=" * 30 + "\n\n"
    
    for volume in novel.volumes.all():
        content += f"\n【{volume.title}】\n\n"
        for chapter in volume.chapters.all():
            content += f"{chapter.title}\n\n"
            paragraphs = chapter.content.split('\n')
            for p in paragraphs:
                p = p.strip()
                if p:
                    content += f"\u3000\u3000{p}\n"
                else:
                    content += "\n"
            content += "\n\n"
            
    response.write(content)
    return response

# ==========================================
# 7. 章节相关的 API 接口
# ==========================================
@login_required
def api_get_chapter(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id, volume__novel__user=request.user)
    return JsonResponse({
        'status': 'success',
        'title': chapter.title,
        'content': chapter.content
    })

@login_required
def api_save_chapter(request, chapter_id):
    if request.method == 'POST':
        chapter = get_object_or_404(Chapter, id=chapter_id, volume__novel__user=request.user)
        data = json.loads(request.body)
        chapter.title = data.get('title', chapter.title)
        chapter.content = data.get('content', chapter.content)
        chapter.save()
        return JsonResponse({
            'status': 'success', 
            'word_count': chapter.word_count,
            'total_words': chapter.volume.novel.total_words
        })
    return JsonResponse({'status': 'error'}, status=400)

# ==========================================
# 8. 卷 / 章节的快速增删
# ==========================================
@login_required
def api_create_chapter(request, volume_id):
    if request.method == 'POST':
        volume = get_object_or_404(Volume, id=volume_id, novel__user=request.user)
        last_chapter = volume.chapters.order_by('-sort_order').first()
        next_order = (last_chapter.sort_order + 1) if last_chapter else 1
        chapter = Chapter.objects.create(volume=volume, title=f"第{next_order}章", sort_order=next_order)
        return JsonResponse({'status': 'success', 'chapter_id': chapter.id})
    return JsonResponse({'status': 'error'}, status=400)
        
@login_required
def api_create_volume(request, novel_id):
    if request.method == 'POST':
        novel = get_object_or_404(Novel, id=novel_id, user=request.user)
        last_volume = novel.volumes.order_by('-sort_order').first()
        next_order = (last_volume.sort_order + 1) if last_volume else 1
        volume = Volume.objects.create(novel=novel, title=f"第{next_order}卷", sort_order=next_order)
        Chapter.objects.create(volume=volume, title="第1章", sort_order=1)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def api_delete_item(request, item_type, item_id):
    if request.method == 'POST':
        if item_type == 'chapter':
            obj = get_object_or_404(Chapter, id=item_id, volume__novel__user=request.user)
        elif item_type == 'volume':
            obj = get_object_or_404(Volume, id=item_id, novel__user=request.user)
        else:
            return JsonResponse({'status': 'error', 'message': '未知类型'}, status=400)
        obj.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

# ==========================================
# 9. 设定集 API 接口
# ==========================================
@login_required
def api_get_settings(request, novel_id):
    novel = get_object_or_404(Novel, id=novel_id, user=request.user)
    category = request.GET.get('category', 'character')
    settings = novel.settings.filter(category=category).values('id', 'title', 'content', 'category')
    return JsonResponse({'status': 'success', 'settings': list(settings)})

@login_required
def api_save_setting(request, novel_id):
    if request.method == 'POST':
        novel = get_object_or_404(Novel, id=novel_id, user=request.user)
        data = json.loads(request.body)
        setting_id = data.get('id')
        title = data.get('title')
        content = data.get('content')
        category = data.get('category', 'character')
        
        if setting_id:
            setting = get_object_or_404(Setting, id=setting_id, novel=novel)
            setting.title = title
            setting.content = content
            setting.category = category  #123
            setting.save()
        else:
            last_setting = novel.settings.filter(category=category).order_by('-sort_order').first()
            next_order = (last_setting.sort_order + 1) if last_setting else 1
            setting = Setting.objects.create(novel=novel, title=title, content=content, category=category, sort_order=next_order)
            
        return JsonResponse({'status': 'success', 'id': setting.id})
    return JsonResponse({'status': 'error'}, status=400)

# ==========================================
# 10. 拖拽排序接口
# ==========================================
@login_required
@require_POST
def api_reorder_items(request, novel_id):
    novel = get_object_or_404(Novel, id=novel_id, user=request.user)
    data = json.loads(request.body)
    item_type = data.get('type')
    orders = data.get('orders', []) 

    if item_type == 'volume':
        for item in orders:
            Volume.objects.filter(id=item['id'], novel=novel).update(sort_order=item['sort_order'])
    elif item_type == 'chapter':
        for item in orders:
            Chapter.objects.filter(id=item['id'], volume__novel=novel).update(sort_order=item['sort_order'])
    elif item_type == 'setting':
        for item in orders:
            Setting.objects.filter(id=item['id'], novel=novel).update(sort_order=item['sort_order'])
            
    return JsonResponse({'status': 'success'})

# 追加在 views.py
@login_required
@require_POST
def api_edit_volume(request, volume_id):
    volume = get_object_or_404(Volume, id=volume_id, novel__user=request.user)
    data = json.loads(request.body)
    title = data.get('title')
    if title:
        volume.title = title
        volume.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)