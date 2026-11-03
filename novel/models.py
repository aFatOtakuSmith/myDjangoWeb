from django.db import models
from django.contrib.auth.models import User

# ==========================================
# 模型 1：小说信息表（存储所有小说）
# ==========================================
class Novel(models.Model):
    STATUS_CHOICES = [
        ('ongoing', '连载中'), 
        ('completed', '已完结')
    ]
    
    title = models.CharField('书名', max_length=100)
    # 关联作者，如果你有多位作者，或者以后开放给别人写
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')
    cover = models.ImageField('封面图', upload_to='novel/covers/', blank=True, null=True)
    summary = models.TextField('简介', max_length=1000, blank=True)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='ongoing')
    
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('最后更新时间', auto_now=True)

    class Meta:
        verbose_name = '小说'
        verbose_name_plural = '小说'
        ordering = ['-updated_at'] # 默认按最近更新排序

    def __str__(self):
        return self.title

    @property
    def total_words(self):
        """动态计算这本书的总字数"""
        return sum(chapter.word_count for chapter in self.chapters.all())

    @property
    def latest_chapter(self):
        """获取最新章节，方便在首页展示"""
        return self.chapters.order_by('-sort_order').first()

# ==========================================
# 模型 2：章节内容表（用来写小说）
# ==========================================
class Chapter(models.Model):
    # 外键关联上面的 Novel，related_name='chapters' 方便反向查询
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='chapters', verbose_name='所属小说')
    title = models.CharField('章节名', max_length=200) # 比如：第一章 初入江湖
    content = models.TextField('正文内容')
    sort_order = models.PositiveIntegerField('章节排序', default=0, help_text='数字越小越靠前')
    word_count = models.PositiveIntegerField('字数', default=0, editable=False)
    created_at = models.DateTimeField('发布时间', auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'created_at'] # 按序号正序排列
        verbose_name = '章节'
        verbose_name_plural = '章节'

    def __str__(self):
        return f"{self.novel.title} - {self.title}"

    def save(self, *args, **kwargs):
        # 🌟 核心逻辑：在保存章节时，自动计算正文字数（去除空格和换行）
        clean_text = self.content.replace('\n', '').replace(' ', '').replace('\r', '')
        self.word_count = len(clean_text)
        super().save(*args, **kwargs)