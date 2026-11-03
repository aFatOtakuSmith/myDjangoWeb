from django.contrib import admin
from django import forms
from .models import Novel, Chapter

# 自定义表单，把正文框拉高
class ChapterAdminForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = '__all__'
        widgets = {
            'content': forms.Textarea(attrs={'rows': 25, 'style': 'width: 100%; font-family: monospace; font-size: 16px; line-height: 1.8;'}),
            'title': forms.TextInput(attrs={'style': 'width: 100%; font-size: 16px;'}),
        }

class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 0
    fields = ('title', 'sort_order', 'word_count')
    readonly_fields = ('word_count',)
    show_change_link = True

@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'total_words', 'updated_at')
    list_filter = ('status', 'author')
    search_fields = ('title', 'summary')
    inlines = [ChapterInline]

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    form = ChapterAdminForm # 🌟 应用自定义的高大文本框
    list_display = ('title', 'novel', 'sort_order', 'word_count', 'created_at')
    list_filter = ('novel',)
    search_fields = ('title', 'content')