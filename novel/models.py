from django.db import models
from django.contrib.auth.models import User

# 1. 书籍 (Book)
class Novel(models.Model):
    STATUS_CHOICES = [('ongoing', '连载中'), ('completed', '已完结')]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    title = models.CharField('书名', max_length=100)
    cover = models.ImageField('封面图', upload_to='novel/covers/', blank=True, null=True)
    summary = models.TextField('简介', max_length=1000, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='ongoing')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('最后更新时间', auto_now=True)

    class Meta:
        verbose_name = '书籍'
        verbose_name_plural = '书籍'
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    @property
    def total_words(self):
        # 动态计算全书总字数
        chapters = Chapter.objects.filter(volume__novel=self)
        return sum(chapter.word_count for chapter in chapters)

# 2. 卷 (Volume) - 比如：第一卷 初入江湖
class Volume(models.Model):
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='volumes', verbose_name='所属书籍')
    title = models.CharField('卷名', max_length=100)
    sort_order = models.PositiveIntegerField('排序(越小越靠前)', default=0)

    class Meta:
        verbose_name = '卷'
        verbose_name_plural = '卷'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f"{self.novel.title} - {self.title}"

# 3. 章节 (Chapter)
class Chapter(models.Model):
    volume = models.ForeignKey(Volume, on_delete=models.CASCADE, related_name='chapters', verbose_name='所属卷')
    title = models.CharField('章节名', max_length=200)
    content = models.TextField('正文内容', blank=True)
    sort_order = models.PositiveIntegerField('排序(越小越靠前)', default=0)
    word_count = models.PositiveIntegerField('字数', default=0, editable=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('最后更新时间', auto_now=True)

    class Meta:
        verbose_name = '章节'
        verbose_name_plural = '章节'
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f"{self.volume.title} - {self.title}"

    def save(self, *args, **kwargs):
        # 自动统计字数（去除空格和换行）
        if self.content:
            clean_text = self.content.replace('\n', '').replace(' ', '').replace('\r', '')
            self.word_count = len(clean_text)
        super().save(*args, **kwargs)

# 4. 设定集 (Setting) - 世界观、角色卡
class Setting(models.Model):
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='settings', verbose_name='所属书籍')
    title = models.CharField('设定名称', max_length=100)
    content = models.TextField('设定内容')
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '设定集'
        verbose_name_plural = '设定集'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.novel.title} - {self.title}"

        # 替换你原本的 Setting 模型
class Setting(models.Model):
    CATEGORY_CHOICES = [
        ('character', '👤 角色档案'),
        ('world', '🌍 世界观'),
        ('item', '⚔️ 道具/物品'),
        ('other', '📝 其他'),
    ]
    
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='settings', verbose_name='所属书籍')
    category = models.CharField('分类', max_length=20, choices=CATEGORY_CHOICES, default='character')
    title = models.CharField('设定名称', max_length=100)
    content = models.TextField('设定内容')
    sort_order = models.PositiveIntegerField('排序', default=0)  # 🌟 新增
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '设定集'
        verbose_name_plural = '设定集'
        ordering = ['sort_order', '-updated_at']  # 🌟 按排序字段优先

    def __str__(self):
        return f"{self.novel.title} - {self.title}"