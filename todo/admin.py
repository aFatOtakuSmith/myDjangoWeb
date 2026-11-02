from django.contrib import admin
from .models import TodoItem, TodoRecord

@admin.register(TodoItem)
class TodoItemAdmin(admin.ModelAdmin):
    list_display = ('content', 'user', 'repeat_type', 'priority', 'is_done', 'due_date')
    list_filter = ('repeat_type', 'priority', 'is_done')
    search_fields = ('content',)

@admin.register(TodoRecord)
class TodoRecordAdmin(admin.ModelAdmin):
    list_display = ('todo', 'date')
    list_filter = ('date',)