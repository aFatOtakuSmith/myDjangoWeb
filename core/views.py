from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session # 🌟 新增：用于操作 Session
from django.utils import timezone # 🌟 新增：用于过滤过期 Session
from .models import QuoteCategory  

def index(request):
    return render(request, 'core/index.html')

def about(request):
    return render(request, 'core/about.html')

def contact(request):
    return render(request, 'core/contact.html')

def quotes_list(request):
    categories = QuoteCategory.objects.all()
    
    current_type_str = request.GET.get('type', '')
    
    if not current_type_str and categories.exists():
        current_type_str = f"sentence_{categories.first().id}"

    real_id = current_type_str.replace('sentence_', '')
    
    quotes = []
    if real_id:
        try:
            category = QuoteCategory.objects.get(id=real_id)
            quotes = category.quotes.all()
        except (QuoteCategory.DoesNotExist, ValueError):
            pass

    return render(request, 'core/quotes.html', {
        'categories': categories,
        'quotes': quotes,
        'current_type_id': current_type_str
    })

# ==========================================
# 🌟 新增：单点登录核心逻辑（踢掉其他设备）
# ==========================================
def kick_other_sessions(user, current_session_key):
    """强制销毁该用户除了当前 session 之外的所有 session"""
    # 获取所有未过期的 session
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    for session in active_sessions:
        data = session.get_decoded()
        # 如果 session 里的 user_id 是当前用户，且不是刚刚生成的那个 session
        if data.get('_auth_user_id') == str(user.id) and session.session_key != current_session_key:
            session.delete()

# 1. 登录页面
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # 🌟 核心：确保新 session 已经写入，并踢掉其他设备
            request.session.save() 
            kick_other_sessions(user, request.session.session_key)
            
            # 检查是否是因为访问受限页面被踢过来的
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('core:profile')
            
        else:
            return render(request, 'core/login.html', {'error': '账号或密码错误'})
            
    return render(request, 'core/login.html')

# 2. 退出登录
def logout_view(request):
    logout(request)
    return redirect('/') 

# 3. 个人主页（🌟 核心：只有管理员 + moxiao 才能进）
@login_required
def profile_view(request):
    # 判断当前登录的用户是不是超级管理员，或者用户名是不是 moxiao
    if request.user.is_superuser or request.user.username == 'moxiao':
        return render(request, 'core/profile.html')
    
    # 如果是其他普通账号登录，提示开发中
    return render(request, 'core/under_development.html')