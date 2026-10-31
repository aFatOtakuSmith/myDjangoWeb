from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Subquery, OuterRef
from .models import DeviceData, DeviceSummary

# 原有的数据后台
@admin.register(DeviceData)
class DeviceDataAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'payload', 'created_at')
    list_filter = ('device_id', 'created_at')
    search_fields = ('device_id',)
    ordering = ('-created_at',)

# 🌟 新增：设备列表代理后台
@admin.register(DeviceSummary)
class DeviceSummaryAdmin(admin.ModelAdmin):
    list_display = ('device_id_link', 'get_data_count', 'get_last_seen')
    
    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return False

    # 核心修复：返回真实的模型实例，避免 _meta 报错
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # 使用子查询，只取出每个设备最新（最后一条）的记录
        latest_records = DeviceData.objects.filter(
            device_id=OuterRef('device_id')
        ).order_by('-created_at').values('id')[:1]
        
        return qs.filter(id__in=Subquery(latest_records)).order_by('-created_at')

    # 1. 设备 ID 变成超链接
    def device_id_link(self, obj):
        base_url = reverse('admin:iot_devicedata_changelist')
        url = f"{base_url}?device_id__exact={obj.device_id}"
        return format_html('<a href="{}" style="font-weight: bold; color: #0ea5e9;">{}</a>', url, obj.device_id)
    device_id_link.short_description = '设备 ID'

    # 2. 动态计算数据总量
    def get_data_count(self, obj):
        return DeviceData.objects.filter(device_id=obj.device_id).count()
    get_data_count.short_description = '数据总量'

    # 3. 最后上报时间
    def get_last_seen(self, obj):
        return obj.created_at
    get_last_seen.short_description = '最后上报时间'