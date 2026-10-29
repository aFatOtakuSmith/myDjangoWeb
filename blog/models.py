import os
import re
import shutil
import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings
from mdeditor.fields import MDTextField

# 🌟 博客分类模型
class BlogCategory(models.Model):
    name = models.CharField('分类名称', max_length=50, unique=True)
    # 🌟 排序字段
    order = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name='排序') 
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        ordering = ['order'] # 按 order 排序
        verbose_name = '博客分类'
        verbose_name_plural = '博客分类'

    def __str__(self):
        return self.name

class BlogPost(models.Model):
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, verbose_name='所属分类', related_name='posts', null=True, blank=True)
    
    # 🌟 排序字段
    order = models.PositiveIntegerField(default=0, blank=False, null=False, verbose_name='排序') 
    
    title = models.CharField('文章标题', max_length=150)
    summary = models.TextField('摘要', max_length=300, blank=True, help_text='显示在列表页的简介')
    content = MDTextField('正文内容 (Markdown)')
    tags = models.CharField('标签', max_length=100, blank=True, help_text='多个标签用英文逗号分隔')
    is_public = models.BooleanField('公开', default=True)
    created_at = models.DateTimeField('发布时间', default=timezone.now)

    class Meta:
        # 🌟 优先按手动排序，其次按时间倒序（保证未拖拽的新文章排前面）
        ordering = ['order', '-created_at'] 
        verbose_name = '博客文章'
        verbose_name_plural = '博客文章'

    def __str__(self):
        return self.title

    @property
    def tag_list(self):
        if self.tags:
            return [t.strip() for t in self.tags.split(',') if t.strip()]
        return []

    def save(self, *args, **kwargs):
        # 1. 基础路径准备
        safe_title = re.sub(r'[^\w\s-]', '', self.title).strip() if self.title else "untitled"
        if not safe_title:
            safe_title = "untitled"
            
        now = timezone.now()
        year = now.strftime('%Y')
        month = now.strftime('%m')
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temps')

        # 2. 转移正文中新上传的临时图片
        if self.content and '/media/temps/' in self.content:
            matches = re.findall(r'/media/temps/([^"\')\s]+)', self.content)
            if matches:
                unique_folder = f"{safe_title}_{uuid.uuid4().hex[:6]}"
                relative_dir = f"blog_uploads/{year}/{month}/{unique_folder}"
                target_dir = os.path.join(settings.MEDIA_ROOT, relative_dir)
                os.makedirs(target_dir, exist_ok=True)

                for filename in matches:
                    temp_file_path = os.path.join(temp_dir, filename)
                    target_file_path = os.path.join(target_dir, filename)
                    
                    if os.path.exists(temp_file_path):
                        shutil.move(temp_file_path, target_file_path)
                    
                    old_path = f"/media/temps/{filename}"
                    new_path = f"/media/{relative_dir}/{filename}"
                    self.content = self.content.replace(old_path, new_path)

        # 3. 保存数据库
        super().save(*args, **kwargs)

        # 4. 智能清理废弃图片
        blog_matches = re.findall(r'/media/(blog_uploads/[^"\')\s]+)', self.content) if self.content else []
        folders_to_check = set()
        for match in blog_matches:
            folder_path = os.path.dirname(match)
            folders_to_check.add(os.path.join(settings.MEDIA_ROOT, folder_path))

        for folder in folders_to_check:
            if os.path.exists(folder):
                for filename in os.listdir(folder):
                    file_path = os.path.join(folder, filename)
                    if os.path.isfile(file_path):
                        if self.content is None or filename not in self.content:
                            try:
                                os.remove(file_path)
                                print(f"已清理废弃博客图片: {filename}")
                            except Exception:
                                pass

    def delete(self, *args, **kwargs):
        if self.content:
            matches = re.findall(r'/media/(blog_uploads/\d{4}/\d{2}/[^/]+)/', self.content)
            if matches:
                unique_folders = set(matches)
                for folder in unique_folders:
                    folder_path = os.path.join(settings.MEDIA_ROOT, folder)
                    if os.path.exists(folder_path):
                        try:
                            shutil.rmtree(folder_path)
                            print(f"已删除文章专属图片文件夹: {folder}")
                        except Exception:
                            pass
        super().delete(*args, **kwargs)