from django.db import models
from django.db.models import Max

def get_next_order():
    max_order = Song.objects.aggregate(Max('my_order'))['my_order__max']
    return (max_order or 0) + 1

class Playlist(models.Model):
    name = models.CharField('歌单名称', max_length=50, unique=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '播放列表'
        verbose_name_plural = '播放列表'
        ordering = ['id']

    def __str__(self):
        return self.name

class Song(models.Model):
    title = models.CharField('歌曲名称', max_length=100)
    file = models.FileField('音乐文件 (MP3)', upload_to='music/')
    
    playlists = models.ManyToManyField(Playlist, blank=True, verbose_name='所属歌单', related_name='songs')
    
    # 🌟 新增：是否喜欢（全局状态）
    is_liked = models.BooleanField('喜欢', default=False)
    
    my_order = models.PositiveIntegerField(
        default=get_next_order, 
        blank=False, 
        null=False,
        db_index=True, 
        verbose_name='排序'
    )
    created_at = models.DateTimeField('上传时间', auto_now_add=True)

    class Meta:
        ordering = ['my_order'] 
        verbose_name = '音乐'
        verbose_name_plural = '音乐'

    def __str__(self):
        return self.title