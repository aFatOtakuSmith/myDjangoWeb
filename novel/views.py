from django.shortcuts import render, get_object_or_404
from .models import Novel, Chapter

def novel_list(request):
    """书库列表页"""
    novels = Novel.objects.all()
    return render(request, 'novel/novel_list.html', {'novels': novels})

def novel_detail(request, pk):
    """小说详情与章节目录页"""
    novel = get_object_or_404(Novel, pk=pk)
    chapters = novel.chapters.all()
    return render(request, 'novel/novel_detail.html', {
        'novel': novel,
        'chapters': chapters
    })

def chapter_read(request, pk):
    """沉浸式阅读页"""
    chapter = get_object_or_404(Chapter, pk=pk)
    novel = chapter.novel
    
    # 自动找上一章：同一本书中，sort_order 比当前小，且最接近当前的一章
    prev_chapter = novel.chapters.filter(sort_order__lt=chapter.sort_order).order_by('-sort_order').first()
    
    # 自动找下一章：同一本书中，sort_order 比当前大，且最接近当前的一章
    next_chapter = novel.chapters.filter(sort_order__gt=chapter.sort_order).order_by('sort_order').first()
    
    return render(request, 'novel/chapter_read.html', {
        'chapter': chapter,
        'novel': novel,
        'prev_chapter': prev_chapter,
        'next_chapter': next_chapter
    })
    