from django.contrib import admin
from .models import Work

@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    # 后台列表显示的字段
    list_display = ('title', 'is_featured', 'created_at')
    
    # 右侧过滤器
    list_filter = ('is_featured', 'created_at')
    
    # 搜索框支持的字段
    search_fields = ('title', 'summary', 'tags')
    
    # 允许在列表页直接修改的字段（可选，方便快速切换主打作品）
    list_editable = ('is_featured',)
    
    # 按时间倒序排列
    ordering = ('-created_at',)

    # =========================================
    # 🌟 核心：注入自定义 CSS 修复 Markdown 弹窗错位
    # =========================================
    class Media:
        css = {
            # 指向刚才创建的修复样式表
            'all': ('works/css/fix_mdeditor.css',)
        }