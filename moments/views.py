from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.db.models import Q, Sum
from django.utils import timezone
from .models import LifeShare


def moments_list(request):
    """生活分享列表页（带作者筛选、搜索和分页）"""
    shares_list = LifeShare.objects.filter(is_public=True).order_by('-created_at')

    query = request.GET.get('q')
    if query:
        shares_list = shares_list.filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__icontains=query)
        )

    author_id = request.GET.get('author_id')
    current_author = None
    if author_id:
        current_author = User.objects.filter(pk=author_id).first()
        if current_author:
            shares_list = shares_list.filter(author=current_author)

    paginator = Paginator(shares_list, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    valid_author_ids = LifeShare.objects.filter(
        is_public=True,
        author__isnull=False
    ).values_list('author_id', flat=True).distinct()

    authors = User.objects.filter(id__in=valid_author_ids)

    return render(request, 'moments/moments_list.html', {
        'page_obj': page_obj,
        'shares': page_obj,
        'authors': authors,
        'current_author': current_author,
        'query': query,
    })


def share_detail(request, pk):
    """文章详情页"""
    share = get_object_or_404(LifeShare, pk=pk, is_public=True)
    return render(request, 'moments/share_detail.html', {'share': share})


def author_detail(request, user_id):
    """作者个人主页（只读）"""
    author = get_object_or_404(User, pk=user_id)

    shares_qs = LifeShare.objects.filter(
        author=author, is_public=True
    ).order_by('-created_at')

    total_shares = shares_qs.count()
    total_read_time = shares_qs.aggregate(
        total=Sum('read_time')
    )['total'] or 0

    # 🌟 改动 4：date_joined 晚于当前时间（系统时间回拨等）时不再显示负数
    joined_days = max(0, (timezone.now() - author.date_joined).days)

    paginator = Paginator(shares_qs, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    profile = getattr(author, 'profile', None)

    return render(request, 'moments/author_detail.html', {
        'author': author,
        'profile': profile,
        'shares': page_obj,
        'page_obj': page_obj,
        'total_shares': total_shares,
        'total_read_time': total_read_time,
        'joined_days': joined_days,
    })