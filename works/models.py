import os
import re
import shutil
import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings
from mdeditor.fields import MDTextField

# 🌟 新增：作品集分类模型
class WorkCategory(models.Model):
    name = models.CharField('作品集名称', max_length=50, unique=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        ordering = ['id']
        verbose_name = '作品集'
        verbose_name_plural = '作品集'

    def __str__(self):
        return self.name

def get_work_cover_path(instance, filename):
    safe_title = re.sub(r'[^\w\s-]', '', instance.title).strip() if instance.title else "untitled"
    if not safe_title:
        safe_title = "untitled"
    now = timezone.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_F_{uuid.uuid4().hex[:6]}{ext}"
    return os.path.join('works_uploads', year, month, safe_title, new_filename)

class Work(models.Model):
    # 🌟 新增：关联作品集，允许为空以兼容旧数据
    category = models.ForeignKey(WorkCategory, on_delete=models.CASCADE, verbose_name='所属作品集', related_name='works', null=True, blank=True)
    
    title = models.CharField('作品名称', max_length=100)
    summary = models.CharField('简短简介', max_length=200, help_text='鼠标悬停时显示的一两句话')
    description = MDTextField('详细描述 (Markdown)', blank=True)
    cover = models.ImageField('封面图', upload_to=get_work_cover_path, blank=True, null=True)
    link = models.URLField('外部链接/GitHub', blank=True, help_text='点击卡片跳转的地址')
    tags = models.CharField('标签', max_length=100, blank=True, help_text='多个标签用英文逗号分隔')
    created_at = models.DateTimeField('发布时间', default=timezone.now)
    is_featured = models.BooleanField('设为主打作品', default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '作品'
        verbose_name_plural = '作品'

    def __str__(self):
        return self.title

    @property
    def tag_list(self):
        if self.tags:
            return [t.strip() for t in self.tags.split(',') if t.strip()]
        return []

    def save(self, *args, **kwargs):
        # 清理旧封面
        if self.pk:
            old_instance = Work.objects.filter(pk=self.pk).first()
            if old_instance and old_instance.cover:
                if old_instance.cover != self.cover:
                    if os.path.isfile(old_instance.cover.path):
                        try:
                            os.remove(old_instance.cover.path)
                        except Exception as e:
                            pass

        safe_title = re.sub(r'[^\w\s-]', '', self.title).strip() if self.title else "untitled"
        if not safe_title:
            safe_title = "untitled"
        now = timezone.now()
        year = now.strftime('%Y')
        month = now.strftime('%m')
        
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temps')

        if self.description and '/media/temps/' in self.description:
            matches = re.findall(r'/media/temps/([^"\')\s]+)', self.description)
            if matches:
                unique_folder = f"{safe_title}_{uuid.uuid4().hex[:6]}"
                relative_dir = f"works_uploads/{year}/{month}/{unique_folder}"
                target_dir = os.path.join(settings.MEDIA_ROOT, relative_dir)
                os.makedirs(target_dir, exist_ok=True)

                for filename in matches:
                    temp_file_path = os.path.join(temp_dir, filename)
                    target_file_path = os.path.join(target_dir, filename)
                    if os.path.exists(temp_file_path):
                        shutil.move(temp_file_path, target_file_path)
                    
                    old_path = f"/media/temps/{filename}"
                    new_path = f"/media/{relative_dir}/{filename}"
                    self.description = self.description.replace(old_path, new_path)

        super().save(*args, **kwargs)

        if self.description:
            blog_matches = re.findall(r'/media/(works_uploads/[^"\')\s]+)', self.description)
            folders_to_check = set()
            for match in blog_matches:
                folder_path = os.path.dirname(match)
                folders_to_check.add(os.path.join(settings.MEDIA_ROOT, folder_path))

            for folder in folders_to_check:
                if os.path.exists(folder):
                    for filename in os.listdir(folder):
                        file_path = os.path.join(folder, filename)
                        if os.path.isfile(file_path) and '_F' not in filename:
                            if filename not in self.description:
                                try:
                                    os.remove(file_path)
                                except Exception:
                                    pass

    def delete(self, *args, **kwargs):
        safe_title = re.sub(r'[^\w\s-]', '', self.title).strip() if self.title else "untitled"
        if not safe_title:
            safe_title = "untitled"
        works_uploads_dir = os.path.join(settings.MEDIA_ROOT, 'works_uploads')
        if os.path.exists(works_uploads_dir):
            for root, dirs, files in os.walk(works_uploads_dir):
                for d in dirs:
                    if d == safe_title or d.startswith(f"{safe_title}_"):
                        folder_to_delete = os.path.join(root, d)
                        try:
                            shutil.rmtree(folder_to_delete)
                        except Exception:
                            pass
                break
        super().delete(*args, **kwargs)