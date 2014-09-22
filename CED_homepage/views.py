# -*- coding:utf-8 -*-
from django.shortcuts import render,render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from CED_homepage.models import *

#权限控制封装
def is_not_admin(view):
    pass


#登陆控制封装
def requirelogin(view):
    pass


#CED首页
def homepage(request):
    #获取所有issues
    allissues=ced_issues.objects.all()
    allevents=ced_events.objects.all()
    hasNoEvent=False

    myevents=[] # 收集我的事件
    for event in allevents:
        #只显示我的事件
        if len(event.user_r.all().filter(username=request.user.username))!=0:
            myevents.append(event)

    myeventsnum = len(myevents) # 事件总数

    if myeventsnum==0:
        hasNoEvent=True

    #获取相关数据
    issue_done_num=allissues.filter(issuestatus=3).count()
    issue_wait_num=allissues.filter(issuestatus=2).count()
    issue_undo_num=allissues.filter(issuestatus=1).count()
    issue_rollback_num=allissues.filter(issuestatus=4).count()
    return render_to_response(
        "homepage.html",
        {
            'Allissues':allissues,
            'issuedone':issue_done_num,
            'issueundo':issue_undo_num,
            'issuewait':issue_wait_num,
            'issuerollback':issue_rollback_num,
            'myevents':myevents[0:10],
            'myeventsnum':myeventsnum,
            'hasEvent':hasNoEvent,
            'curuser':request.user,
        }

    )

#用于工具的实时输出
def redis_io_info(request):
    pass

#详情页处理
def ced_issue_detail(request,cedis):
    hasNoEvent=False

    #获取到id
    cedisid=cedis[5:]
    allevents=ced_events.objects.all()
    myevents=[] #收集我的事件

    for event in allevents:
        #只显示我的事件
        if len(event.user_r.all().filter(username=request.user.username))!=0:
            myevents.append(event)
    myeventsnum=len(myevents) #事件总数
    if myeventsnum==0:
        hasNoEvent=True
    cedisone=ced_issues.objects.get(id=cedisid)
    return render_to_response("cedisdetail.html",
        {
            "thiscedis":cedisone,
            'myevents':myevents[0:10],
            'myeventsnum':myeventsnum,
            'hasEvent':hasNoEvent,
            'curuser':request.user,
        }
    )

#显示我的所有事件列表
def ced_show_allmyevents(request):
    hasNoEvent=False

    #获取我所有的事件信息
    allevents=ced_events.objects.all()
    myevents=[] #收集我的事件
    for event in allevents:
        #只显示我的事件
        if len(event.user_r.all().filter(username=request.user.username))!=0:
            myevents.append(event)
    myeventsnum=len(myevents) #事件总数

    if myeventsnum==0:
        hasNoEvent=True

    return render_to_response("myevents.html",{
            'myevents':myevents[0:10],
            'myeventsnum':myeventsnum,
            'hasEvent':hasNoEvent,
            'myallevents':myevents,
            'curuser':request.user,
    })

#Ajax推送评论消息
def ced_ajax_addnewcomment(request,cedis):

    if request.method == "POST" and request.FILES.get("commentfile"):

        upfile=request.FILES["commentfile"]

        if not upfile.name.lower().endswith(('.png','.jpg','.jpeg','.gif')):
            return render_to_response("errorinfo.html",
                    {'errorinfo':u"不支持的文件上传类型！"},
                )
        elif upfile.size/1024>1024:
            return render_to_response("errorinfo.html",
                    {'errorinfo':u"附件大小不得大于1MB，请重新选择附件！"},
                )
        elif request.POST["commentcontent"]=="":
            return render_to_response("errorinfo.html",
                    {'errorinfo':u"评论内容不能为空！"},
                )
        else:
            newcomment=ced_issue_comments(
                commentman=AuthUser.objects.get(username=request.user.username),
                comment=request.POST["commentcontent"],
                commentattach=upfile,
            )
            try:
                newcomment.save()
                #绑定到这个cedis上
                cis=ced_issues.objects.get(id=cedis[5:])
                cis.issuecomments.add(newcomment)
            except:
                return render_to_response("errorinfo.html",
                    {'errorinfo':u"远程服务器错误！请联系管理员"},
                )
            else:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    elif request.POST["commentfile"] == "" and request.POST["commentcontent"] != "":
            newcomment=ced_issue_comments(
                commentman=AuthUser.objects.get(username=request.user.username),
                comment=request.POST["commentcontent"],
            )
            try:
                newcomment.save()
                #绑定到这个cedis上
                cis=ced_issues.objects.get(id=cedis[5:])
                cis.issuecomments.add(newcomment)
            except:
                return render_to_response("errorinfo.html",
                    {'errorinfo':u"远程服务器错误！请联系管理员"},
                )
            else:
                #直接跳转
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        return render_to_response("errorinfo.html",
                    {'errorinfo':u"非法请求！评论内容不能为空！"},
                )


#分类issue筛选
def show_cat_issues(request,cattype):

    hasNoEvent=False

    """分类显示"""
    try:
        u_issue_status=int(cattype)
        c_issues=ced_issues.objects.all().filter(issuestatus=u_issue_status)

        #获取所有issues
        allissues=ced_issues.objects.all()
        allevents=ced_events.objects.all()

        myevents=[] #收集我的事件
        for event in allevents:
            #只显示我的事件
            if len(event.user_r.all().filter(username=request.user.username))!=0:
                myevents.append(event)

        myeventsnum=len(myevents) #事件总数

        if myeventsnum==0:
            hasNoEvent=True

        #获取相关数据
        issue_done_num=allissues.filter(issuestatus=3).count()
        issue_wait_num=allissues.filter(issuestatus=2).count()
        issue_undo_num=allissues.filter(issuestatus=1).count()
        issue_rollback_num=allissues.filter(issuestatus=4).count()

        return render_to_response(
            "homepage.html",
            {
                'Allissues':c_issues,
                'issuedone':issue_done_num,
                'issueundo':issue_undo_num,
                'issuewait':issue_wait_num,
                'issuerollback':issue_rollback_num,
                'myevents':myevents[0:10],
                'myeventsnum':myeventsnum,
                'hasEvent':hasNoEvent,
                'curuser':request.user,
            }

        )
    except:
        return Http404()


#通知对方的实现,ajax
def ced_ajax_notify(request,cedis):
    """通知对方"""
    if request.method=="POST":
        thisissue_id=cedis[5:]
        thisissue=ced_issues.objects.get(id=thisissue_id) #定位该问题单
        thisissue_current_status=thisissue.issuestatus
        if thisissue_current_status==2 or thisissue_current_status==3:
            return HttpResponse(u"当前状态无需通知！")
        else:
            try:
                thisissue.issuestatus=2 #置为待确认
                thisissue.save() #保存并触发事件通知
            except:
                return HttpResponse(u"通知过程中发生异常")
            else:
                return HttpResponse(u"通知成功,请等待对方确认!")
    else:
        return HttpResponse(u"非法请求")


#搜索直达功能
def ced_search_issue(request):
    pass


#ajax定时拉取事件
def ced_ajax_get_eventlists(request):
    """返回JSON数据,给前端解析"""
    if request.method=="POST":
        pass


#获取英雄榜列表
def ced_get_hero_lists(request):

    hasNoEvent=False

    #获取我所有的事件信息
    allevents = ced_events.objects.all()
    myevents = []   # 收集我的事件
    for event in allevents:
        #只显示我的事件
        if len(event.user_r.all().filter(username=request.user.username)) != 0:
            myevents.append(event)
    myeventsnum=len(myevents) #事件总数

    if myeventsnum==0:
        hasNoEvent=True

    #获取到所有管理员
    heros=CedEnvAdminGroup.objects.all()

    return render_to_response(
        "envadmins.html",

        {
            'heros':heros,
            'myevents':myevents[0:10],
            'myeventsnum':myeventsnum,
            'hasEvent':hasNoEvent,
            'myallevents':myevents,
            'curuser':request.user,

        }
    )


#数据展示页面
def ced_show_alldatas(request):

    hasNoEvent=False

    #获取我所有的事件信息
    allevents = ced_events.objects.all()
    myevents = []   # 收集我的事件
    for event in allevents:
        #只显示我的事件
        if len(event.user_r.all().filter(username=request.user.username)) != 0:
            myevents.append(event)
    myeventsnum=len(myevents) #事件总数

    if myeventsnum==0:
        hasNoEvent=True

    return render_to_response(
        "datas.html",
        {
            'myevents':myevents[0:10],
            'myeventsnum':myeventsnum,
            'hasEvent':hasNoEvent,
            'myallevents':myevents,
            'curuser':request.user,
        }
    )


#环境管理员个人设置页面
def ced_person_config(request):

    hasNoEvent=False

    #获取我所有的事件信息
    allevents = ced_events.objects.all()
    myevents = []   # 收集我的事件
    for event in allevents:
        #只显示我的事件
        if len(event.user_r.all().filter(username=request.user.username)) != 0:
            myevents.append(event)
    myeventsnum=len(myevents) #事件总数

    thisadmin=CedEnvAdminGroup.objects.get(envadminname=request.user)

    if myeventsnum==0:
        hasNoEvent=True

    return render_to_response(
        "adminsetting.html",
        {
            'myevents':myevents[0:10],
            'myeventsnum':myeventsnum,
            'hasEvent':hasNoEvent,
            'myallevents':myevents,
            'thisadmin':thisadmin,
            'curuser':request.user,
        }
    )


#管理员个人设置页面的ajax接口
def ced_ajax_save_admin_settings(request):
    if request.method=="POST" and request.POST["avatarurl"]!="" and request.POST["status"]!="":
        thisadmin=CedEnvAdminGroup.objects.get(envadminname=request.user)
        thisadmin.envadminavatar=request.POST["avatarurl"]
        thisadmin.envadminstatus=request.POST["status"]
        try:
            thisadmin.save()
        except:
            return HttpResponse(u"保存修改时发生错误!")
        else:
            return HttpResponse(u"保存成功!")
    else:
        return HttpResponse(u"啊哦，你好像忘了填写什么或者勾选什么？")


#ajax提交新的问题单页面
def ced_ajax_new_issue_submit(request):

    hasNoEvent=False

    allcedtypes=ced_types.objects.all()

    #获取我所有的事件信息
    allevents = ced_events.objects.all()
    myevents = []   # 收集我的事件
    for event in allevents:
        #只显示我的事件
        if len(event.user_r.all().filter(username=request.user.username)) != 0:
            myevents.append(event)
    myeventsnum=len(myevents) #事件总数

    #获取到所有管理员
    heros=CedEnvAdminGroup.objects.all()

    if myeventsnum==0:
        hasNoEvent=True

    return render_to_response(
        "newissue.html",
        {
            'heros':heros,
            'myevents':myevents[0:10],
            'myeventsnum':myeventsnum,
            'hasEvent':hasNoEvent,
            'myallevents':myevents,
            'curuser':request.user,
            'allcedtypes':allcedtypes,

        }
    )


def ced_ajax_save_new_issue(request):

    """后端提交新issue的验证"""

    cedtmpkeys=[]

    if request.method == "POST":

        if request.POST["newistitle"]=="": #判断标题是否为空
            return render_to_response("errorinfo.html",
                        {'errorinfo':u"标题不能为空！"},
                )
        elif request.POST["newisdes"]=="": #判断描述是否为空
            return render_to_response("errorinfo.html",
                        {'errorinfo':u"描述不能为空！"},
                )
        elif request.POST["newistype"]=="": #验证环境类型
            return render_to_response("errorinfo.html",
                        {'errorinfo':u"类型不能为空！"},
                )
        elif request.POST["whoischoosed"]=="":
            return render_to_response("errorinfo.html",
                        {'errorinfo':u"接受处理人不能为空！"},
                )
        elif request.FILES.has_key("file"):

            upfile=request.FILES["file"]

            if not upfile.name.lower().endswith(('.png','.jpg','.jpeg','.gif')):
                return render_to_response("errorinfo.html",
                    {'errorinfo':u"不支持的文件上传类型！"},
                )
            elif upfile.size/1024>1024:
                return render_to_response("errorinfo.html",
                    {'errorinfo':u"附件大小不得大于1MB，请重新选择附件！"},
                )
        try:
            ced_types.objects.get(issuetype=request.POST["newistype"])
            AuthUser.objects.get(username=request.POST["whoischoosed"])
        except:
            return render_to_response("errorinfo.html",
                        {'errorinfo':u"请检查环境问题类型和问题接收人是否正确！"},
                )
        else:
            newissue=ced_issues(
                issuetitle=request.POST["newistitle"],
                issuedetail=request.POST["newisdes"],
                issuetypes=ced_types.objects.get(issuetype=request.POST["newistype"]),
                issuesubman=AuthUser.objects.get(username=request.user.username), #提交人必须是当前用户
                issueattach=request.FILES["file"] if request.FILES.has_key("file") else "", #附件保存
            )

            newissue.save() #先保存,加入issuereceivemans,问题单接收人,逻辑为有且只能选择一个
            newissue.issuereceivemans.add(AuthUser.objects.get(username=request.POST["whoischoosed"]))

            try:
                #获取分隔后的tag线索，然后加入issuekey
                for item in request.POST['newistag'].split(" "):
                    cedtmpkeys.append(ced_keys(keyname=item))

                for obj in cedtmpkeys:
                    obj.save() #先保存
                    newissue.issuekey.add(obj) #在加入到issue的key中来

                #触发模型信号事件
                newissue.save()

            except:
                return render_to_response("errorinfo.html",
                        {'errorinfo':u"远程服务器错误！请联系管理员"},
                )

            else:
                #直接返回首页
                return HttpResponseRedirect("/")
    else:
        return render_to_response("errorinfo.html",
                    {'errorinfo':u"非法请求!"},
                )


def ced_ajax_save_commentfile(request):
    pass

def ced_ajax_clear_all_notify(request):
    """消除所有的通知"""
    pass