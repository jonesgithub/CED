# -*- coding:utf-8 -*-

from django.shortcuts import render
from django.shortcuts import HttpResponseRedirect,HttpResponse
from django.shortcuts import render_to_response

#imports
import requests
import json
import xmlrpclib

def codesync_home_page(request):
    all_fat_env_info=requests.get("http://192.168.81.146:9001/env/GetEnvSub?envid=1")
    #env_detail_info=requests.get("http://192.168.81.146:9001/env/GetDeployDomainByEnv?envid=112")
    return render_to_response("codesync.html",{
        'allinfolist':json.loads(all_fat_env_info.content)["SubEnvs"],
        #'envdetaillist':json.loads(env_detail_info.content)["Configs"]
    })

def ajax_get_domainconfig(request,domainname):
    resbody=requests.get("http://192.168.81.146:9001/env/GetDomainConfig?domainname="+domainname)
    return HttpResponse(resbody.content,content_type="application/json") #返回JSON数据

def ajax_get_env_detail(request,envid):
    env_detail_info=requests.get("http://192.168.81.146:9001/env/GetDeployDomainByEnv?envid="+envid)
    return HttpResponse(env_detail_info.content,content_type="application/json")

def single_site_sync(request):
    """根据syncdst得到src对应的站点,如果无则返回对应信息"""
    if 'sitename' in request.POST and request.POST['sitename']:
        sitename=request.POST['sitename']
        envsubname=requests.get("http://192.168.81.146:9001/env/GetDomainConfig?domainname="+sitename)
        ENVSUBNAME=json.loads(envsubname.content)["Configs"][0]["EnvSubName"]
        dstserver=json.loads(envsubname.content)["Configs"][0]["IPAddress"]
        dstsitename=json.loads(envsubname.content)["Configs"][0]["DomainName"]
        srcsitename=json.loads(envsubname.content)["Configs"][0]["DomainName"].replace(ENVSUBNAME,"fat2")
        res2=json.loads(requests.get("http://192.168.81.146:9001/env/GetDomainConfig?domainname="+srcsitename).content)
        if res2["StateCode"]==0: #正确
            srcserver=res2["Configs"][0]["IPAddress"]
        elif res2["StateCode"]==1: #存在错误码
            return HttpResponse(u"未找到同步源的对应站点!")
        #开始同步
        server = xmlrpclib.ServerProxy(r"http://"+dstserver+":7999")
        try:
            if server.start_sync(r"\\"+srcserver+"\\WebSites\\"+srcsitename,r"D:\\WebSites\\"+dstsitename):
                server.update_configs(r"D:\\WebSites\\"+dstsitename,'fat2',ENVSUBNAME) #开始回调配置刷新
                return HttpResponse(u"同步完成!")
            else:
                return HttpResponse(u"同步过程中发生错误!")
        except:
            return HttpResponse(u"Agent连接异常!")

def ajax_get_xmlrpc_run_info(request):
    pass