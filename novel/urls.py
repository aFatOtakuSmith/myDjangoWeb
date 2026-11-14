from django.urls import path
from . import views

app_name = 'novel'

urlpatterns = [
    path('', views.novel_list, name='novel_list'),
    path('create/', views.create_novel, name='create_novel'),
    path('edit/<int:novel_id>/', views.edit_novel, name='edit_novel'),
    path('delete/<int:novel_id>/', views.delete_novel, name='delete_novel'),
    path('write/<int:novel_id>/', views.write_book, name='write_book'),
    path('export/<int:novel_id>/', views.export_txt, name='export_txt'),
    
    # 章节及拖拽 API
    path('api/get/chapter/<int:chapter_id>/', views.api_get_chapter, name='api_get_chapter'),
    path('api/save/chapter/<int:chapter_id>/', views.api_save_chapter, name='api_save_chapter'),
    path('api/create/chapter/<int:volume_id>/', views.api_create_chapter, name='api_create_chapter'),
    path('api/create/volume/<int:novel_id>/', views.api_create_volume, name='api_create_volume'),
    path('api/delete/<str:item_type>/<int:item_id>/', views.api_delete_item, name='api_delete_item'),
    path('api/reorder/<int:novel_id>/', views.api_reorder_items, name='api_reorder_items'),
    
    # 设定集 API
    path('api/settings/<int:novel_id>/', views.api_get_settings, name='api_get_settings'),
    path('api/settings/<int:novel_id>/save/', views.api_save_setting, name='api_save_setting'),
    # 追加在 urls.py
    path('api/edit/volume/<int:volume_id>/', views.api_edit_volume, name='api_edit_volume'),
]