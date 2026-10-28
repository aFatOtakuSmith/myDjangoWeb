import os
import re
import shutil
import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings
from mdeditor.fields import MDTextField

def get_work_cover_path(instance, filename):
    # 处理标题，防止特殊字符
    safe_title = re.sub(r'[^\w\s-]', '', instance.title).strip() if instance.title else "untitled"
    if not safe_title:
        safe_title = "untitled"
    
    now = timezone.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    
    # 分离文件名和后缀，并在末尾加上 _F 和随机码防止同名覆盖
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_F_{uuid.uuid4().hex[:6]}{ext}"
    
    # 最终路径：works_uploads/2026/10/作品名/封面_F_随机码.jpg
    return os.path.join('works_uploads', year, month, safe_title, new_filename)


class Work(models.Model):
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
        # =========================================
        # 🌟 1. 清理被替换的旧封面图
        # =========================================
        if self.pk:
            old_instance = Work.objects.filter(pk=self.pk).first()
            if old_instance and old_instance.cover:
                if old_instance.cover != self.cover:
                    if os.path.isfile(old_instance.cover.path):
                        try:
                            os.remove(old_instance.cover.path)
                        except Exception as e:
                            print(f"删除旧封面失败: {e}")

        # =========================================
        # 🌟 2. 转移刚上传的 Markdown 临时图片（使用唯一标识符防止同名冲突）
        # =========================================
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
                # 生成形如：作品名_a1b2c3 的唯一文件夹
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

        # =========================================
        # 3. 正常保存数据库
        # =========================================
        super().save(*args, **kwargs)

        # =========================================
        # 🌟 4. 智能清理正文中被用户删掉的废弃图片
        # =========================================
        if self.description:
            # 提取正文中引用的所有 works_uploads 路径
            blog_matches = re.findall(r'/media/(works_uploads/[^"\')\s]+)', self.description)
            
            folders_to_check = set()
            for match in blog_matches:
                folder_path = os.path.dirname(match)
                folders_to_check.add(os.path.join(settings.MEDIA_ROOT, folder_path))

            for folder in folders_to_check:
                if os.path.exists(folder):
                    for filename in os.listdir(folder):
                        file_path = os.path.join(folder, filename)
                        # 只处理文件，且跳过带 _F 的封面图
                        if os.path.isfile(file_path) and '_F' not in filename:
                            if filename not in self.description:
                                try:
                                    os.remove(file_path)
                                    print(f"已清理正文中被删除的废弃图片: {filename}")
                                except Exception as e:
                                    print(f"清理图片失败: {e}")

    def delete(self, *args, **kwargs):
        # 🌟 智能删除：清理与文章相关的封面文件夹和正文图文件夹
        safe_title = re.sub(r'[^\w\s-]', '', self.title).strip() if self.title else "untitled"
        if not safe_title:
            safe_title = "untitled"

        works_uploads_dir = os.path.join(settings.MEDIA_ROOT, 'works_uploads')
        
        if os.path.exists(works_uploads_dir):
            # 遍历查找所有名字以“作品名”开头的文件夹并删除
            # 这包含了“作品名”（封面所在）和“作品名_hash”（正文图所在）
            for root, dirs, files in os.walk(works_uploads_dir):
                for d in dirs:
                    if d == safe_title or d.startswith(f"{safe_title}_"):
                        folder_to_delete = os.path.join(root, d)
                        try:
                            shutil.rmtree(folder_to_delete)
                            print(f"已彻底删除作品图片文件夹: {d}")
                        except Exception:
                            pass
                break # 只在最底层的年份/月份目录下进行扫描（防止递归太深误删）

        super().delete(*args, **kwargs)