from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from .models import Work, WorkCategory

@admin.register(WorkCategory)
class WorkCategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    # 🌟 移除了 order，由插件接管
    list_display = ('name', 'get_work_count')
    
    def get_work_count(self, obj):
        return obj.works.count()
    get_work_count.short_description = '作品数量'

@admin.register(Work)
class WorkAdmin(SortableAdminMixin, admin.ModelAdmin):
    # 🌟 移除了 order，移除了原有的 ordering = ('-created_at',)，否则会和拖拽冲突
    list_display = ('title', 'category', 'is_featured', 'created_at')
    list_filter = ('category', 'is_featured', 'created_at')
    search_fields = ('title', 'summary', 'tags')
    list_editable = ('is_featured',)

    class Media:
        css = {
            'all': ('works/css/fix_mdeditor.css',)
        }