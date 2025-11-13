from django.contrib import admin

# Register your models here.
from .models import DeviceDB, DeviceType, MetricType, DeviceMetric, MetricMapping, Vendor

admin.site.register(DeviceDB)
admin.site.register(DeviceType)
admin.site.register(MetricType)
admin.site.register(DeviceMetric)
admin.site.register(MetricMapping)
admin.site.register(Vendor)