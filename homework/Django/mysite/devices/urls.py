# devices/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('collect/', views.collect_once, name='collect_once'),
    path("add/", views.add_device, name="add_device"),
    path("", views.device_list, name="device_list"),  # 新增列表页 URL
    path("devices/<int:device_id>/edit/", views.edit_device, name="edit_device"),
    path('devices/delete/<int:pk>/', views.delete_device, name='delete_device')

]
