from django.contrib import admin
from django import forms
from .models import QuoteCategory, Quote

# 🌟 自定义表单：单行输入，排除自动生成的时间
class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['content', 'author']
        widgets = {
            'content': forms.TextInput(attrs={'style': 'width: 100%; padding: 5px;'}),
        }

# 🌟 嵌套表单：在分类页面直接显示句子、作者、只读时间
class QuoteInline(admin.TabularInline):
    model = Quote
    form = QuoteForm
    extra = 1
    fields = ('content', 'author', 'get_created_at')
    
    # 🌟 核心：展示自定义的时间列，并设为只读
    readonly_fields = ('get_created_at',)
    
    verbose_name = '句子'
    verbose_name_plural = '分类下的句子'

    # 定义一个方法格式化时间，让后台看起来更美观
    def get_created_at(self, obj):
        if obj.created_at:
            return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
        return "-"
    get_created_at.short_description = '加入时间'

# 🌟 分类后台管理
@admin.register(QuoteCategory)
class QuoteCategoryAdmin(admin.ModelAdmin):
    # 🌟 修改 1：把 name 放在第一位，id 放后面
    list_display = ('name', 'id', 'get_quote_count') 
    
    # 🌟 修改 2：明确告诉 Django，把 name 变成超链接
    list_display_links = ('name',) 
    
    inlines = [QuoteInline]

    def get_quote_count(self, obj):
        return obj.quotes.count()
    get_quote_count.short_description = '句子数量'

# 🌟 句子后台管理（单独查看时的列表）
@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    form = QuoteForm
    list_display = ('category', 'content', 'author', 'get_created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('content', 'author')
    
    def get_created_at(self, obj):
        if obj.created_at:
            return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
        return "-"
    get_created_at.short_description = '加入时间'