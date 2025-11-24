import hashlib
from django.db import models

def file_upload_path(instance, filename):
    return f"uploads/{filename}"

class Document(models.Model):
    filename = models.CharField(max_length=255)
    file = models.FileField(upload_to=file_upload_path)
    file_hash = models.CharField(max_length=64, unique=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # 计算文件 hash，用于阻止重复上传 , 在 Django 中，save() 方法会在你 显式或隐式保存模型实例到数据库 时被调用。
        hasher = hashlib.sha256()
        for chunk in self.file.chunks():
            hasher.update(chunk)
        self.file_hash = hasher.hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.filename
