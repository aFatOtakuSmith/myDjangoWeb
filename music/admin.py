from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from django.utils.html import format_html
from django.urls import reverse
from .models import Song, Playlist

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Song)
class SongAdmin(SortableAdminMixin, admin.ModelAdmin):
    # 🌟 增加 is_liked 展示，并允许直接编辑
    list_display = ('title', 'my_order', 'is_liked', 'created_at')
    list_editable = ('my_order', 'is_liked')
    search_fields = ('title',)
    filter_horizontal = ('playlists',)
    
    def has_add_permission(self, request):
        return False

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        try:
            upload_url = reverse('music:batch_upload')
            extra_context['batch_upload_btn'] = format_html(
                '<a href="{}" class="button" style="background: #0ea5e9; color: white; padding: 10px 20px; border-radius: 5px; font-weight: bold; text-decoration: none;">🚀 批量导入音乐</a>', 
                upload_url
            )
        except Exception:
            pass
        return super().changelist_view(request, extra_context=extra_context)