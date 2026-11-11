from django.db import models
from django.contrib.auth.models import User
import os

# ==========================================
# 🌟 动态路径：media/ai_chat/AI名字/文件名
# ==========================================
def get_upload_path(instance, filename):
    # 清理名字中的非法字符，防止路径错误
    folder_name = "".join([c for c in instance.name if c.isalnum() or c in (' ', '_', '-')]).strip()
    if not folder_name:
        folder_name = "unnamed_agent"
    return os.path.join('ai_chat', folder_name, filename)


# ==========================================
# 1. AI 角色表（兼容角色卡的所有字段）
# ==========================================
class AIAgent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者')
    name = models.CharField('AI 名称', max_length=50)
    
    # 图片字段
    avatar = models.ImageField(
        '头像 (小图)', 
        upload_to=get_upload_path, 
        blank=True, null=True,
    )
    portrait = models.ImageField(
        '立绘 (大图)', 
        upload_to=get_upload_path, 
        blank=True, null=True,
    )

    # 基础设定（手工填写时用这个）
    system_prompt = models.TextField('角色设定 (System Prompt)', blank=True)
    
    # 🌟 角色卡（SillyTavern）专用扩展字段
    description = models.TextField('外貌与背景', blank=True, null=True)
    personality = models.TextField('性格特点', blank=True, null=True)
    scenario = models.TextField('当前场景', blank=True, null=True)
    mes_example = models.TextField('对话示例', blank=True, null=True)
    character_book = models.JSONField('内嵌世界书 (JSON)', blank=True, null=True)

    # API 与模型参数
    api_key = models.CharField('API 密钥', max_length=200, blank=True, null=True, help_text='留空则使用系统默认')
    temperature = models.FloatField('创造力(温度)', default=0.8, help_text='0.0 严谨，1.0 发散')
    max_tokens = models.IntegerField('最大回复长度', default=2048, help_text='限制 AI 单次回复的字数')
    
    # 对话相关
    greeting = models.CharField('开场白', max_length=500, default='你好，我是你的专属 AI。', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = 'AI 角色'
        verbose_name_plural = 'AI 角色'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    # 重写 delete 方法：删库的同时，把服务器上的图片文件也删了
    def delete(self, *args, **kwargs):
        if self.avatar and os.path.isfile(self.avatar.path):
            try: os.remove(self.avatar.path)
            except: pass
        if self.portrait and os.path.isfile(self.portrait.path):
            try: os.remove(self.portrait.path)
            except: pass
        super().delete(*args, **kwargs)


# ==========================================
# 2. 聊天会话表
# ==========================================
class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户', related_name='chat_sessions')
    agent = models.ForeignKey(AIAgent, on_delete=models.CASCADE, verbose_name='关联 AI', related_name='sessions')
    title = models.CharField('会话标题', max_length=100, default='新对话')
    is_pinned = models.BooleanField('是否置顶', default=False)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('最后更新时间', auto_now=True)

    class Meta:
        verbose_name = '聊天会话'
        verbose_name_plural = '聊天会话'
        ordering = ['-is_pinned', '-updated_at']

    def __str__(self):
        return f"{self.user.username} - {self.agent.name} - {self.title}"


# ==========================================
# 3. 聊天消息表
# ==========================================
class ChatMessage(models.Model):
    ROLE_CHOICES = [('system', '系统'), ('user', '用户'), ('assistant', 'AI')]
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, verbose_name='所属会话', related_name='messages')
    role = models.CharField('角色', max_length=20, choices=ROLE_CHOICES)
    content = models.TextField('消息内容')
    reasoning_content = models.TextField('思考过程 (Reasoning)', blank=True, null=True)
    token_usage = models.IntegerField('消耗Token', default=0)
    created_at = models.DateTimeField('发送时间', auto_now_add=True)

    class Meta:
        verbose_name = '聊天消息'
        verbose_name_plural = '聊天消息'
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:20]}..."


# ==========================================
# 4. 提示词模板表 (预留功能)
# ==========================================
class PromptTemplate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者')
    title = models.CharField('模板名称', max_length=50)
    content = models.TextField('模板内容')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '提示词模板'
        verbose_name_plural = '提示词模板'

    def __str__(self):
        return self.title