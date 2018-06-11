# -*- coding:utf-8 -*-

# a mini Django project

import sys
from django.shortcuts import render
from django.conf import settings
from django.conf.urls import url
from django.http import HttpResponse
from django.core.management import execute_from_command_line

settings.configure(
        DEBUG = True, # 调试状态
        SECRET_KEY = 'iamasecretkeyhahahaha', # 默认的session需要的key，也为了CSRF
        ROOT_URLCONF = sys.modules[__name__], # url根目录的配置
    )

def home(request):
    #return HttpResponse('a mini django website')  # 主页
    return render(request, "index.html")
urlpatterns = [
        url(r'^$', home,name='home'), # 元组类型，默认请求发送到home函数
    ]

# 启动程序
if __name__ == "__main__":
    execute_from_command_line(sys.argv)