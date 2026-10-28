from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# ==========================================
# 0. 头像统一目录：media/head/<user_id>/<filename>
# ==========================================
def avatar_upload_to(instance, filename):
    # """
    # 头像统一存放到 media/head/ 下，按 user_id 分子目录。
    # - 正常情况：instance.user.id 存在 → head/12/xxx.jpg
    # - 极端情况：user 还没保存（理论上不会发生，因为 Profile 是内联在 User 表单里的）
    #             → 退化为 head/shared/xxx.jpg
    # """
    user_id = getattr(instance.user, 'id', None) or 'shared'
    return f"head/{user_id}/{filename}"


# ==========================================
# 1. 作者档案模型（关联系统 User）
# ==========================================
class AuthorProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='profile', verbose_name='用户'
    )
    nickname = models.CharField('昵称', max_length=50, blank=True)
    avatar = models.ImageField(
        '头像',
        upload_to=avatar_upload_to,      # ← 关键：统一到 media/head/
        blank=True,
        null=True,
    )
    bio = models.TextField('个人简介', max_length=200, blank=True)

    class Meta:
        verbose_name = '作者档案'
        verbose_name_plural = '作者档案'

    def __str__(self):
        return self.nickname or self.user.username


# ==========================================
# 2. 文章模型（封面照旧：media/lifeshare/年/月/）
# ==========================================
class LifeShare(models.Model):
    """生活分享文章"""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='作者', related_name='shares',
        null=True, blank=True,
    )

    title = models.CharField('标题', max_length=120)
    summary = models.TextField('摘要', max_length=300, blank=True)
    content = models.TextField('正文', blank=True)
    cover = models.ImageField(
        '封面图',
        upload_to='lifeshare/%Y/%m/',     # ← 封面保持原样，不用动
        blank=True, null=True,
    )
    tags = models.CharField(
        '标签', max_length=200, blank=True,
        help_text='多个标签用英文逗号分隔',
    )
    read_time = models.PositiveIntegerField('阅读时长(分钟)', default=5)
    is_public = models.BooleanField('公开', default=True)
    created_at = models.DateTimeField('发布时间', default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '生活分享'
        verbose_name_plural = '生活分享'

    def __str__(self):
        return self.title

    @property
    def tag_list(self):
        if self.tags:
            return [t.strip() for t in self.tags.split(',') if t.strip()]
        return []