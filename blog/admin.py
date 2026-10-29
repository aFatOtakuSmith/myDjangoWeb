from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from .models import BlogPost, BlogCategory

@admin.register(BlogCategory)
class BlogCategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    # 🌟 去掉了 order，让插件自动接管左侧的拖拽
    list_display = ('name', 'get_post_count') 
    
    def get_post_count(self, obj):
        return obj.posts.count()
    get_post_count.short_description = '文章数量'

@admin.register(BlogPost)
class BlogPostAdmin(SortableAdminMixin, admin.ModelAdmin):
    # 🌟 去掉了 order，让插件自动接管左侧的拖拽
    list_display = ('title', 'category', 'is_public', 'created_at')
    list_filter = ('category', 'is_public', 'created_at')
    search_fields = ('title', 'summary', 'content')
    date_hierarchy = 'created_at'