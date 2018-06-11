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

def index(request):
    return render(request, "index.html")

# 遍历指定目录，显示目录下的所有文件名
def eachFile():
    filepath="data"
    pathDir =  os.listdir(filepath)
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

'''
def dealfile():
    i = 1
    dic = []
    poem = ""
    f = open("data\modelA.txt", "r", encoding="utf-8")
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
            list = [id, poem]
            dic.append(list)
            poem = ""
        i = i + 1
    return dic
'''

# Build response data structure
def responseData(idx, totallist):
    i = idx * PER_PAGE
    temp = {'errcode': 200,
            'id': idx,
            'data': {
                'poems': []
            }
            }
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
def getInitData():
    print('获取数据 -----------')
    #print(cache.get('init_data'))
    if not cache.get('init_data'):
        totallist = eachFile()
        cache.set('init_data', totallist, 3600)
    else:
        totallist = cache.get('init_data')
    return totallist


# 初始获取数据
def getData(request):
    # TODO: 获取初始数据
    totallist = getInitData()
    id = 0
    resp = responseData(id, totallist)
    return HttpResponse(json.dumps(resp), content_type="application/json")


# 提交评分并且返回下次数据
def postData(request):
    if request.method == 'POST':
        req = json.loads(request.body)

        # TODO: 保存数据
        print(req)
        username=str(req['author'])
        for i in range(len(req['poems'])):
            title=str(req['poems'][i]['keywords']).split(" ")[0]
            keyword=str(req['poems'][i]['keywords'])[len(title):]
            modelname=str(req['poems'][i]['model'])

            score_a=str(req['poems'][i]['score']['a'])
            score_b=str(req['poems'][i]['score']['b'])
            score_c=str(req['poems'][i]['score']['b'])
            score_total=str(req['poems'][i]['total'])

            resultfile = "resultdata\\" + username + "-" + modelname + nowtime
            f=open(resultfile,"a+",encoding="utf-8")
            f.write(title+":"+score_a+"+"+score_b+"+"+score_c+"="+score_total+"\n")
            f.write(keyword+"\n")
            f.write(req['poems'][i]['content']+"\n")

        # TODO: 获取下一组诗歌
        totallist = getInitData()
        current = req['currentPage']
        resp = responseData(current, totallist)
        return HttpResponse(json.dumps(resp), content_type="application/json")
