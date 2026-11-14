from django.contrib import admin
from .models import Novel, Volume, Chapter, Setting

# 🌟 内联章节，在“卷”里面可以直接添加章节
class ChapterInline(admin.TabularInline):
    model = Chapter
    extra = 0
    fields = ('title', 'sort_order', 'word_count', 'updated_at')
    readonly_fields = ('word_count', 'updated_at')
    show_change_link = True

# 🌟 内联卷，在“书”里面可以直接添加卷
class VolumeInline(admin.TabularInline):
    model = Volume
    extra = 0
    show_change_link = True

@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'total_words', 'updated_at')
    list_filter = ('status', 'user')
    search_fields = ('title', 'summary')
    inlines = [VolumeInline]

@admin.register(Volume)
class VolumeAdmin(admin.ModelAdmin):
    list_display = ('title', 'novel', 'sort_order')
    list_filter = ('novel',)
    inlines = [ChapterInline]

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'volume', 'word_count', 'updated_at')
    list_filter = ('volume__novel',)
    search_fields = ('title', 'content')
    
    # 把后台的输入框拉大，方便在后台直接改
    def formfield_for_dbfield(self, db_field, **kwargs):
        from django import forms
        if db_field.name == 'content':
            kwargs['widget'] = forms.Textarea(attrs={'rows': 30, 'style': 'width: 100%; font-family: monospace; font-size: 16px;'})
        return super().formfield_for_dbfield(db_field, **kwargs)

@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('title', 'novel', 'updated_at')
    search_fields = ('title', 'content')