from django.urls import path
from . import views

app_name = 'filecenter'

urlpatterns = [
    path('upload/', views.upload_files, name="upload"),
    path('list/', views.file_list, name="list"),
    path('download/<int:pk>/', views.download_file, name="download"),
    path('delete/<int:pk>/', views.delete_file, name="delete"),
]
