from django.contrib import admin
from .models import Work, WorkCategory

@admin.register(WorkCategory)
class WorkCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_work_count')
    
    def get_work_count(self, obj):
        return obj.works.count()
    get_work_count.short_description = '作品数量'

@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_featured', 'created_at')
    # 🌟 加上分类过滤
    list_filter = ('category', 'is_featured', 'created_at')
    search_fields = ('title', 'summary', 'tags')
    list_editable = ('is_featured',)
    ordering = ('-created_at',)

    class Media:
        css = {
            'all': ('works/css/fix_mdeditor.css',)
        }