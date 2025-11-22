from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("data/", views.dashboard_data, name="dashboard_data"),
    path("ultimate_line", views.ultimate_line, name="ultimate_line"),
    path("data/cpu/", views.cpu_data_api, name="cpu_data_api"),
    path("area-simple", views.area_simple, name="area-simple"),
    path("final_line_if_speed",views.qyt_device_echarts_final_line_if_speed_class, name="qyt_device_echarts_final_line_if_speed_url"),
    path("data/final_line_if_speed/", views.final_line_if_speed_data_api, name="final_line_if_speed_data_api"),
]
