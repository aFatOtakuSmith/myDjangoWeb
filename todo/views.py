from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import TodoItem, TodoRecord
from datetime import date, timedelta
from django.utils import timezone

# ================= 1. 待办列表页 =================
@login_required
def todo_list(request):
    if not (request.user.is_superuser or request.user.username == 'moxiao'):
        return redirect('core:under_development')

    today = date.today()
    weekday = today.isoweekday()

    if request.method == 'POST':
        if 'delete_todo' in request.POST:
            item_id = request.POST.get('item_id')
            TodoItem.objects.filter(id=item_id, user=request.user).delete()
            
        elif 'toggle_todo' in request.POST:
            item_id = request.POST.get('item_id')
            item = get_object_or_404(TodoItem, id=item_id, user=request.user)
            
            if item.repeat_type == 'none' or not item.repeat_type:
                item.is_done = not item.is_done
                item.completed_at = timezone.now() if item.is_done else None
                item.save()
            else:
                record, created = TodoRecord.objects.get_or_create(todo=item, date=today)
                if not created:
                    record.delete()
            
        return redirect('todo:todo_list') # 🌟 确保带 todo: 前缀

    # 获取普通待办
    normal_todos = TodoItem.objects.filter(user=request.user, repeat_type='none', is_done=False)
    
    # 获取周期习惯
    recurring_todos = TodoItem.objects.filter(user=request.user, repeat_type__in=['daily', 'weekly', 'range'])
    
    today_recurring = []
    for task in recurring_todos:
        should_show = False
        if task.repeat_type == 'daily':
            should_show = True
        elif task.repeat_type == 'weekly':
            if str(weekday) in (task.repeat_days or '').split(','):
                should_show = True
        elif task.repeat_type == 'range':
            if task.start_date and task.end_date and task.start_date <= today <= task.end_date:
                should_show = True
            elif not task.start_date:
                should_show = True
        
        if should_show:
            task.is_checked_today = TodoRecord.objects.filter(todo=task, date=today).exists()
            today_recurring.append(task)

    # 普通待办分组
    overdue, today_list, tomorrow_list, future_list = [], [], [], []
    tomorrow = today + timedelta(days=1)
    
    for todo in normal_todos:
        # 对没有日期字段的旧数据兜底
        if not todo.due_date:
            todo.due_date = today
            todo.save()
            
        if todo.due_date < today: 
            overdue.append(todo)
        elif todo.due_date == today: 
            today_list.append(todo)
        elif todo.due_date == tomorrow: 
            tomorrow_list.append(todo)
        else: 
            future_list.append(todo)

    done_todos = TodoItem.objects.filter(user=request.user, repeat_type='none', is_done=True).order_by('-completed_at')[:5]

    return render(request, 'todo/todo_list.html', {
        'today_recurring': today_recurring,
        'overdue': overdue, 'today_list': today_list, 'tomorrow_list': tomorrow_list,
        'future_list': future_list, 'done_todos': done_todos,
    })

# ================= 2. 独立的新增任务页 =================
@login_required
def todo_add(request):
    if not (request.user.is_superuser or request.user.username == 'moxiao'):
        return redirect('core:under_development')

    if request.method == 'POST':
        content = request.POST.get('content')
        repeat_type = request.POST.get('repeat_type', 'none')
        priority = request.POST.get('priority', 'M')
        category = request.POST.get('category', 'life')
        description = request.POST.get('description', '')
        
        if content:
            task = TodoItem(
                user=request.user, content=content, priority=priority,
                category=category, repeat_type=repeat_type, description=description
            )

            if repeat_type == 'none':
                task.due_date = request.POST.get('due_date') or date.today()
            elif repeat_type == 'daily':
                task.start_date = date.today()
            elif repeat_type == 'weekly':
                days = request.POST.getlist('weekday')
                if not days: days = [str(date.today().isoweekday())]
                task.repeat_days = ",".join(days)
                task.start_date = date.today()
            elif repeat_type == 'range':
                task.start_date = request.POST.get('start_date') or date.today()
                task.end_date = request.POST.get('end_date') or date.today()

            task.save()
            # 🌟 保存成功后重定向，带前缀
            return redirect('todo:todo_list')

    today_str = date.today().strftime('%Y-%m-%d')
    return render(request, 'todo/todo_add.html', {'today_str': today_str})

@login_required
def todo_edit(request, pk):
    if not (request.user.is_superuser or request.user.username == 'moxiao'):
        return redirect('core:under_development')

    # 获取对应的任务，确保只能修改自己的
    task = get_object_or_404(TodoItem, id=pk, user=request.user)

    if request.method == 'POST':
        task.content = request.POST.get('content')
        task.repeat_type = request.POST.get('repeat_type', 'none')
        task.priority = request.POST.get('priority', 'M')
        task.category = request.POST.get('category', 'life')
        task.description = request.POST.get('description', '')

        if task.repeat_type == 'none':
            task.due_date = request.POST.get('due_date') or date.today()
            # 清理周期字段
            task.start_date = None
            task.end_date = None
            task.repeat_days = None
        elif task.repeat_type == 'daily':
            task.start_date = task.start_date or date.today()
            task.due_date = None
            task.end_date = None
            task.repeat_days = None
        elif task.repeat_type == 'weekly':
            days = request.POST.getlist('weekday')
            if not days: days = [str(date.today().isoweekday())]
            task.repeat_days = ",".join(days)
            task.start_date = task.start_date or date.today()
            task.due_date = None
            task.end_date = None
        elif task.repeat_type == 'range':
            task.start_date = request.POST.get('start_date') or date.today()
            task.end_date = request.POST.get('end_date') or date.today()
            task.due_date = None
            task.repeat_days = None

        task.save()
        return redirect('todo:todo_list')

    today_str = date.today().strftime('%Y-%m-%d')
    return render(request, 'todo/todo_edit.html', {
        'task': task,
        'today_str': today_str,
        # 把 repeat_days 拆分好传给前端，用于勾选星期
        'repeat_days_list': (task.repeat_days or '').split(',')
    })