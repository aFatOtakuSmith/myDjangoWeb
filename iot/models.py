from django.db import models

class DeviceData(models.Model):
    device_id = models.CharField('设备ID', max_length=50)
    payload = models.JSONField('上报数据') # 直接存整个 JSON
    created_at = models.DateTimeField('接收时间', auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '设备数据'
        verbose_name_plural = '设备数据'

    def __str__(self):
        return f"{self.device_id} - {self.created_at.strftime('%m-%d %H:%M:%S')}"

class DeviceSummary(DeviceData):
    class Meta:
        proxy = True
        verbose_name = '设备列表'
        verbose_name_plural = '设备列表'