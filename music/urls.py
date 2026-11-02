from django.urls import path
from . import views

app_name = 'music'

urlpatterns = [
    path('', views.music_player, name='music_player'),
    path('batch_upload/', views.batch_upload, name='batch_upload'),
    path('lyrics/<int:song_id>/', views.get_lyrics, name='get_lyrics'),
    path('toggle_like/<int:song_id>/', views.toggle_like, name='toggle_like'), # 🌟 新增路由
]