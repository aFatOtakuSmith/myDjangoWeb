from django.db import models

# 🌟 分类模型
class QuoteCategory(models.Model):
    name = models.CharField('分类名称', max_length=50, unique=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        ordering = ['id']
        verbose_name = '句子分类'
        verbose_name_plural = '句子分类'

    def __str__(self):
        return f"{self.id}. {self.name}"

# 🌟 句子模型
class Quote(models.Model):
    category = models.ForeignKey(QuoteCategory, on_delete=models.CASCADE, verbose_name='所属分类', related_name='quotes')
    content = models.TextField('句子内容')
    author = models.CharField('出处/作者', max_length=100, blank=True)
    created_at = models.DateTimeField('添加时间', auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = '句子'
        verbose_name_plural = '句子'

    def __str__(self):
        return self.content[:20]