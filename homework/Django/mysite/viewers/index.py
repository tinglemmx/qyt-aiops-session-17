from django.shortcuts import render


def index(request):
    context = {
        "qyt_title": "强化班作业Title",
        "qyt_body": "强化班作业Body"
    }
    return render(request, 'index.html',context)