from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class TodoItem(models.Model):
    # ... (保留之前的字段定义) ...
    
    PRIORITY_CHOICES = [('H', '🔥 高'), ('M', '⚡ 中'), ('L', '🌱 低')]
    CATEGORY_CHOICES = [('work', '工作'), ('life', '生活'), ('study', '学习'), ('other', '其他')]
    REPEAT_CHOICES = [('none', '不重复'), ('daily', '每天'), ('weekly', '每周指定天数'), ('range', '指定日期范围每天')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='所属用户')
    content = models.CharField('待办事项', max_length=200)
    due_date = models.DateField('截止日期', null=True, blank=True)
    priority = models.CharField('优先级', max_length=1, choices=PRIORITY_CHOICES, default='M')
    category = models.CharField('分类', max_length=20, choices=CATEGORY_CHOICES, default='life')
    description = models.TextField('详细备注', blank=True, null=True)
    is_done = models.BooleanField('是否完成', default=False)
    completed_at = models.DateTimeField('实际完成时间', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    repeat_type = models.CharField('重复类型', max_length=10, choices=REPEAT_CHOICES, default='none')
    repeat_days = models.CharField('每周哪几天(1-7)', max_length=20, blank=True, null=True)
    start_date = models.DateField('周期开始', null=True, blank=True)
    end_date = models.DateField('周期结束', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '待办/习惯'
        verbose_name_plural = '待办/习惯'

    def __str__(self):
        return self.content

    @property
    def completed_count(self):
        if self.repeat_type == 'none' or not self.repeat_type:
            return 1 if self.is_done else 0
        return self.records.count()

    @property
    def missed_count(self):
        today = timezone.now().date()
        
        if self.repeat_type == 'none' or not self.repeat_type:
            if self.due_date and self.due_date < today and not self.is_done:
                return 1
            return 0
            
        # 防止旧数据没有 created_at
        base_date = self.created_at.date() if self.created_at else today
        start = self.start_date or base_date
        end = today - timedelta(days=1)
        
        if start > end:
            return 0 
            
        total_expected = 0
        current = start
        while current <= end:
            if self.repeat_type == 'daily':
                total_expected += 1
            elif self.repeat_type == 'weekly':
                if str(current.isoweekday()) in (self.repeat_days or '').split(','):
                    total_expected += 1
            elif self.repeat_type == 'range':
                if self.start_date and self.end_date and self.start_date <= current <= self.end_date:
                    total_expected += 1
            current += timedelta(days=1)
            
        actual_completed = self.records.filter(date__gte=start, date__lte=end).count()
        missed = total_expected - actual_completed
        return max(0, missed)

class TodoRecord(models.Model):
    todo = models.ForeignKey(TodoItem, on_delete=models.CASCADE, related_name='records', verbose_name='所属任务')
    date = models.DateField('打卡日期')
    
    class Meta:
        unique_together = ('todo', 'date')
        verbose_name = '打卡记录'
        verbose_name_plural = '打卡记录'

    def __str__(self):
        return f"{self.todo.content} - {self.date}"