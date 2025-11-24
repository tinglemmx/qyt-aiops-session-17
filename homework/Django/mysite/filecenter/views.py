import os
from django.http import FileResponse, HttpResponse
from django.shortcuts import render, redirect,get_object_or_404
from .models import Document
from django.contrib import messages


ALLOWED_EXT = ["doc", "docx"]

def upload_files(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        success_files = []
        for file in files:
            ext = file.name.split('.')[-1].lower()

            # 扩展名限制
            if ext not in ALLOWED_EXT:
                messages.error(request, f"不允许的扩展名：{ext}")
                continue  # 收集错误，继续处理下一个文件

            # 计算 hash 检查重复
            import hashlib
            hasher = hashlib.sha256()
            for chunk in file.chunks():
                hasher.update(chunk)
            file_hash = hasher.hexdigest()

            if Document.objects.filter(file_hash=file_hash).exists():
                messages.error(request, f"文件已存在：{file.name}")
                continue

            # 保存新文件
            doc = Document(filename=file.name, file=file)
            doc.save()
            success_files.append(file.name)

        if success_files:
             messages.success(request, f"{len(success_files)} 个文件上传成功：{', '.join(success_files)}")

        return redirect('filecenter:upload')  # POST-Redirect-GET 防止重复提交
    return render(request, 'filecenter/upload.html')


def file_list(request):
    files = Document.objects.all().order_by('-uploaded_at')
    return render(request, 'filecenter/list.html', {"files": files})


def download_file(request, pk):
    doc = Document.objects.get(pk=pk)
    response = FileResponse(doc.file.open('rb'))
    response['Content-Disposition'] = f'attachment; filename="{doc.filename}"'
    return response


def delete_file(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    doc.file.delete(save=False)  # 删除实际文件
    doc.delete()                 # 删除数据库记录
    messages.success(request, f"文件 '{doc.filename}' 删除成功！")
    return redirect('filecenter:list')
