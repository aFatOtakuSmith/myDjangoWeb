from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import LifeShare, AuthorProfile

# ==========================================
# 1. 用户管理扩展（带作者档案与防越权控制）
# ==========================================
class ProfileInline(admin.StackedInline):
    model = AuthorProfile
    can_delete = False
    verbose_name_plural = '作者信息 (头像与简介)'
    # 把 user 字段设为只读，防止下拉框出现！
    readonly_fields = ('user',) 

class CustomUserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'get_nickname', 'get_avatar', 'is_staff', 'is_superuser')

    def get_nickname(self, obj):
        return obj.profile.nickname if hasattr(obj, 'profile') else '-'
    get_nickname.short_description = '昵称'

    def get_avatar(self, obj):
        if hasattr(obj, 'profile') and obj.profile.avatar:
            return format_html('<img src="{}" style="width: 30px; height: 30px; border-radius: 50%; object-fit: cover;" />', obj.profile.avatar.url)
        return "无"
    get_avatar.short_description = '头像'

    # 1. 列表隔离：非超管只能看到自己
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(pk=request.user.pk)

    # 2. 限制权限：非超管不能新增、不能删除用户
    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    # 3. 限制修改：非超管只能修改自己
    def has_change_permission(self, request, obj=None):
        if obj is not None:
            if not request.user.is_superuser and obj != request.user:
                return False
        return super().has_change_permission(request, obj)

    # 4. 限制字段：普通员工不能修改用户名和权限状态
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return super().get_readonly_fields(request, obj)
        return ('username', 'is_staff', 'is_superuser', 'groups', 'user_permissions', 'last_login', 'date_joined')

    # 5. 允许普通员工看到“用户”菜单
    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        if request.user.is_staff:
            return True
        return super().has_module_permission(request)

# 重新注册 User
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# ==========================================
# 2. 单独注册作者档案（彻底防越权）
# ==========================================
@admin.register(AuthorProfile)
class AuthorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nickname', 'bio')
    search_fields = ('user__username', 'nickname')

    # 非超管直接隐藏左侧的“作者档案”菜单
    def has_module_permission(self, request):
        return request.user.is_superuser

    # 限制列表：非超管只能看到自己的档案
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    # 限制字段：非超管不能修改绑定的用户
    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        return ('user',)
    
    # 限制修改：非超管只能修改自己的档案
    def has_change_permission(self, request, obj=None):
        if obj is not None:
            if not request.user.is_superuser and obj.user != request.user:
                return False
        return super().has_change_permission(request, obj)


# ==========================================
# 3. 生活分享文章管理（🌟 补全了这部分！）
# ==========================================
@admin.register(LifeShare)
class LifeShareAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'read_time', 'is_public', 'created_at')
    list_filter = ('is_public', 'author', 'created_at')
    search_fields = ('title', 'summary', 'content')

    # 限制模块可见性：只有拥有发文权限（或超管）才能看到这个模块
    def has_module_permission(self, request):
        return request.user.is_superuser or request.user.has_perm('moments.add_lifeshare')

    # 限制添加权限
    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.has_perm('moments.add_lifeshare')

    # 数据隔离：普通用户只能看到自己的文章
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)

    # 拦截越权修改：普通用户不能修改别人的文章
    def has_change_permission(self, request, obj=None):
        if obj is not None:
            if not request.user.is_superuser and obj.author != request.user:
                return False
        return super().has_change_permission(request, obj)

    # 拦截越权删除：普通用户不能删除别人的文章
    def has_delete_permission(self, request, obj=None):
        if obj is not None:
            if not request.user.is_superuser and obj.author != request.user:
                return False
        return super().has_delete_permission(request, obj)

    # 动态隐藏作者字段
    def get_exclude(self, request, obj=None):
        if request.user.is_superuser:
            return []
        return ('author',)

    # 自动保存并绑定作者
    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)