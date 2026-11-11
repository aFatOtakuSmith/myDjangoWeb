from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.utils import timezone
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
        'categories': categories, 'quotes': quotes, 'current_type_id': current_type_str
    })

# ==========================================
# 🌟 单点登录核心逻辑（踢掉其他设备）
# ==========================================
def kick_other_sessions(user, current_session_key):
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    for session in active_sessions:
        data = session.get_decoded()
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
            request.session.save() 
            kick_other_sessions(user, request.session.session_key)
            
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

# 3. 个人主页（🌟 所有人登录后都可以进入）
@login_required
def profile_view(request):
    # 计算显示名称
    display_name = request.user.username
    if hasattr(request.user, 'profile') and request.user.profile.nickname:
        display_name = request.user.profile.nickname
    elif request.user.first_name:
        display_name = request.user.first_name
        
    # 直接渲染，不再做拦截
    return render(request, 'core/profile.html', {'display_name': display_name})