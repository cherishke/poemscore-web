import json
import urllib.request
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.core.serializers.json import json
from django.core.cache import cache
import os
import random
import time

# Create your views here.

# Data counts in perpage
PER_PAGE = 3
nowtime=str(time.time())

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
FILE_ROOT = os.path.join(PROJECT_ROOT, 'data')
OUTPUT_ROOT = os.path.join(PROJECT_ROOT, 'resultdata')

def index(request):
    nowtime = str(time.time())
    return render(request, "index.html")

# 遍历指定目录，显示目录下的所有文件名
def eachFile(arr):
    # 传入 selected

    filepath="data"
    pathDir = os.listdir(filepath)
    totallist = []
    for allDir in pathDir:
        realpath = os.path.join(FILE_ROOT, allDir)
        modelName=allDir.split(".")[0]
        i=1
        poem = ""
        f=open(realpath,"r",encoding="utf-8")
        for line in f.readlines():
            if i % 9 == 1:
                linelist = line.split(":")
                id = linelist[0] + " "
            if i % 9 == 2:
                keywordlist = line.split(":")
                id += keywordlist[1].strip()
            if i % 9 > 2 and i % 9 < 9:
                poem += line
            if i % 9 == 0:
                list = [modelName, id, poem]
                totallist.append(list)
                poem = ""
            i = i + 1
    random.shuffle(totallist)
    return totallist

# Build response data structure
def responseData(idx, totallist):
    i = idx * PER_PAGE
    temp = {'errcode': 200,
            'id': idx,
            'data': {
                'poems': []
            }}
    count = 0
    while count < PER_PAGE:
        if ((i + count) < len(totallist)):
            temp['data']['poems'].append({
                'model':totallist[i+count][0],
                'keywords': totallist[i + count][1],
                'content': totallist[i + count][2],
            })
        count = count + 1
    return temp


# 统一获取数据方式
def getInitData(data):
    print('获取数据 -----------')
    CACHE_TAG = 'init_data_' + data['name']
    print(CACHE_TAG)
    if not cache.get(CACHE_TAG):
        totallist = eachFile(data['selected'])
        cache.set(CACHE_TAG, totallist, 3600)
    else:
        totallist = cache.get(CACHE_TAG)
    return totallist

def getlist(request):
    filepath = "data"
    pathDir = os.listdir(filepath)
    return HttpResponse(json.dumps(pathDir), content_type="application/json")

# 初始获取数据
def getData(request):
    if request.method == 'POST':
        req = json.loads(request.body)
        # TODO: 获取初始数据
        totallist = getInitData(req)
        id = 0
        resp = responseData(id, totallist)
        return HttpResponse(json.dumps(resp), content_type="application/json")


# 提交评分并且返回下次数据
def postData(request):
    if request.method == 'POST':
        req = json.loads(request.body)

        # TODO: 保存数据
        username=str(req['author'])
        for i in range(len(req['poems'])):
            title=str(req['poems'][i]['keywords']).split(" ")[0]
            keyword=str(req['poems'][i]['keywords'])[len(title):]
            modelname=str(req['poems'][i]['model'])

            score_a=str(req['poems'][i]['score']['a'])
            score_b=str(req['poems'][i]['score']['b'])
            score_c=str(req['poems'][i]['score']['b'])
            score_total=str(req['poems'][i]['total'])

            resultfile = os.path.join(OUTPUT_ROOT, username + "-" + modelname + nowtime)
            f=open(resultfile,"a+",encoding="utf-8")
            f.write(title+":"+score_a+"+"+score_b+"+"+score_c+"="+score_total+"\n")
            f.write(keyword+"\n")
            f.write(req['poems'][i]['content']+"\n")

        # TODO: 获取下一组诗歌
        totallist = getInitData(req)
        current = req['currentPage']
        resp = responseData(current, totallist)
        return HttpResponse(json.dumps(resp), content_type="application/json")
