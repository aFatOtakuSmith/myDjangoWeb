from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import AIAgent, ChatSession, ChatMessage, PromptTemplate


@admin.register(AIAgent)
class AIAgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    search_fields = ('name', 'system_prompt')
    
    # 🌟 1. 隐藏 'user' 字段，后台不显示下拉框
    exclude = ('user',)

    # 🌟 2. 将 API Key 渲染为密码框，保护密钥
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'api_key':
            kwargs['widget'] = forms.PasswordInput(render_value=True)
        return super().formfield_for_dbfield(db_field, **kwargs)

    # 🌟 3. 保存时自动将当前登录用户设为创建者
    def save_model(self, request, obj, form, change):
        if not change:  # 只有在“新增”时才自动赋值
            obj.user = request.user
        super().save_model(request, obj, form, change)

    # 🌟 4. 数据隔离：非超管只能看到自己创建的 AI
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    # 🌟 5. 重写页面渲染：注入本地图片实时预览的 HTML 和 JS
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        
        # 如果是修改页面，尝试获取现有图片的 URL 用于回显
        avatar_url = ""
        portrait_url = ""
        if object_id:
            obj = self.model.objects.get(id=object_id)
            if obj.avatar:
                avatar_url = obj.avatar.url
            if obj.portrait:
                portrait_url = obj.portrait.url

        # 注入预览框和原生 JS
        extra_context['preview_html'] = format_html("""
            <div style="display:flex; gap:30px; margin-bottom:20px; padding:15px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px;">
                <div style="text-align:center;">
                    <p style="margin:0 0 10px 0; color:#475569; font-weight:bold;">头像实时预览</p>
                    <img id="preview-avatar" src="{}" style="width:100px; height:100px; object-fit:cover; border-radius:8px; border:2px dashed #cbd5e1; background:#fff;">
                </div>
                <div style="text-align:center;">
                    <p style="margin:0 0 10px 0; color:#475569; font-weight:bold;">立绘实时预览</p>
                    <img id="preview-portrait" src="{}" style="width:200px; height:200px; object-fit:contain; border-radius:8px; border:2px dashed #cbd5e1; background:#fff;">
                </div>
            </div>
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    // 监听头像文件选择
                    var avatarInput = document.querySelector('#id_avatar');
                    if (avatarInput) {{
                        avatarInput.addEventListener('change', function(e) {{
                            if (e.target.files && e.target.files[0]) {{
                                var reader = new FileReader();
                                reader.onload = function(e) {{
                                    document.getElementById('preview-avatar').src = e.target.result;
                                }};
                                reader.readAsDataURL(e.target.files[0]);
                            }}
                        }});
                    }}
                    
                    // 监听立绘文件选择
                    var portraitInput = document.querySelector('#id_portrait');
                    if (portraitInput) {{
                        portraitInput.addEventListener('change', function(e) {{
                            if (e.target.files && e.target.files[0]) {{
                                var reader = new FileReader();
                                reader.onload = function(e) {{
                                    document.getElementById('preview-portrait').src = e.target.result;
                                }};
                                reader.readAsDataURL(e.target.files[0]);
                            }}
                        }});
                    }}
                }});
            </script>
        """, 
        # 如果有图片则显示图片URL，没有则使用一个 base64 的透明 1x1 占位图
        avatar_url if avatar_url else "data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==", 
        portrait_url if portrait_url else "data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==")

        return super().changeform_view(request, object_id, form_url, extra_context)


# ==========================================
# 其他模型的后台配置
# ==========================================

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('role', 'content', 'reasoning_content', 'token_usage', 'created_at')
    can_delete = False # 聊天记录通常不建议在后台误删，可视情况开启

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'agent', 'is_pinned', 'updated_at')
    list_filter = ('agent', 'is_pinned', 'user')
    search_fields = ('title',)
    inlines = [ChatMessageInline]

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'content_preview', 'created_at')
    list_filter = ('role', 'session__agent')
    search_fields = ('content',)

    def content_preview(self, obj):
        # 截断过长的消息，让后台列表更美观
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = '消息内容'

@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    search_fields = ('title', 'content')
    
    # 同样限制非管理员只能看自己的模板
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
        
    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user
        super().save_model(request, obj, form, change)