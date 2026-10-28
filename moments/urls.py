from django.urls import path
from . import views

app_name = 'moments'

urlpatterns = [
    path('', views.moments_list, name='moments_list'),
    path('share/<int:pk>/', views.share_detail, name='share_detail'),
    path('author/<int:user_id>/', views.author_detail, name='author_detail'),
]