import os
import re
import shutil
from django.db import models
from django.utils import timezone
from django.conf import settings
from mdeditor.fields import MDTextField

def get_work_cover_path(instance, filename):
    safe_title = re.sub(r'[^\w\s-]', '', instance.title).strip() if instance.title else "untitled"
    if not safe_title:
        safe_title = "untitled"
    now = timezone.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_F{ext}"
    return os.path.join('works_uploads', year, month, safe_title, new_filename)

class Work(models.Model):
    title = models.CharField('作品名称', max_length=100)
    summary = models.CharField('简短简介', max_length=200, blank=True)
    description = MDTextField('详细描述 (Markdown)', blank=True)
    cover = models.ImageField('封面图', upload_to=get_work_cover_path, blank=True, null=True)
    link = models.URLField('外部链接/GitHub', blank=True)
    tags = models.CharField('标签', max_length=100, blank=True)
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
        # =========================================
        # 🌟 1. 新增：清理被替换的旧封面图
        # =========================================
        if self.pk:
            # 如果存在主键，说明是修改，去数据库里查一下旧的数据
            old_instance = Work.objects.filter(pk=self.pk).first()
            if old_instance and old_instance.cover:
                # 如果旧封面存在，且路径跟这次要保存的新封面不一样，说明用户换图了
                if old_instance.cover != self.cover:
                    if os.path.isfile(old_instance.cover.path):
                        try:
                            os.remove(old_instance.cover.path)
                        except Exception as e:
                            print(f"删除旧封面失败: {e}")

        # =========================================
        # 🌟 2. 转移刚上传的 Markdown 临时图片
        # =========================================
        safe_title = re.sub(r'[^\w\s-]', '', self.title).strip() if self.title else "untitled"
        if not safe_title:
            safe_title = "untitled"
        now = timezone.now()
        year = now.strftime('%Y')
        month = now.strftime('%m')
        relative_dir = f"works_uploads/{year}/{month}/{safe_title}"
        target_dir = os.path.join(settings.MEDIA_ROOT, relative_dir)
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temps')

        if self.description and '/media/temps/' in self.description:
            matches = re.findall(r'/media/temps/([^"\')\s]+)', self.description)
            if matches:
                os.makedirs(target_dir, exist_ok=True)
                for filename in matches:
                    temp_file_path = os.path.join(temp_dir, filename)
                    target_file_path = os.path.join(target_dir, filename)
                    if os.path.exists(temp_file_path):
                        shutil.move(temp_file_path, target_file_path)
                    
                    old_path = f"/media/temps/{filename}"
                    new_path = f"/media/{relative_dir}/{filename}"
                    self.description = self.description.replace(old_path, new_path)

        # =========================================
        # 3. 正常保存数据库
        # =========================================
        super().save(*args, **kwargs)

        # =========================================
        # 🌟 4. 清理被用户从正文中删掉的废弃图片
        # =========================================
        if os.path.exists(target_dir):
            for filename in os.listdir(target_dir):
                file_path = os.path.join(target_dir, filename)
                # 只处理文件，且跳过封面图（带 _F 的）
                if os.path.isfile(file_path) and '_F' not in filename:
                    if self.description is None or filename not in self.description:
                        try:
                            os.remove(file_path)
                            print(f"已清理正文中被删除的废弃图片: {filename}")
                        except Exception as e:
                            print(f"清理图片失败: {e}")

    def delete(self, *args, **kwargs):
        safe_title = re.sub(r'[^\w\s-]', '', self.title).strip() if self.title else "untitled"
        if not safe_title:
            safe_title = "untitled"
        works_uploads_dir = os.path.join(settings.MEDIA_ROOT, 'works_uploads')
        if os.path.exists(works_uploads_dir):
            for root, dirs, files in os.walk(works_uploads_dir):
                if safe_title in dirs:
                    folder_to_delete = os.path.join(root, safe_title)
                    shutil.rmtree(folder_to_delete)
                    break
        super().delete(*args, **kwargs)