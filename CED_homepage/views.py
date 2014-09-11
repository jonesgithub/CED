# -*- coding:utf-8 -*-
from django.shortcuts import render,render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from CED_homepage.models import *
from forms import *
from django.template import RequestContext

#CED首页
def homepage(request):
    #获取所有issues
    allissues=ced_issues.objects.all()
    allevents=ced_events.objects.all()
    hasNoEvent=False

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
            'Allissues':allissues,
            'issuedone':issue_done_num,
            'issueundo':issue_undo_num,
            'issuewait':issue_wait_num,
            'issuerollback':issue_rollback_num,
            'myevents':myevents[0:10],
            'myeventsnum':myeventsnum,
            'hasEvent':hasNoEvent
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
    cF=commentForm(data={
        'commentcontent':u' '
    })
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
            'commentform':cF,
            'hasEvent':hasNoEvent
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
    })

#Ajax推送评论消息
def ced_ajax_addnewcomment(request,cedis):
    if request.method=="POST":
        cf=commentForm(request.POST)
        if cf.is_valid(): #如果验证成功
            cd=cf.cleaned_data
            newcomment=ced_issue_comments(
                commentman=AuthUser.objects.get(username=request.user.username),
                comment=cd["commentcontent"]
            )
            try:
                newcomment.save()
                #绑定到这个cedis上
                cis=ced_issues.objects.get(id=cedis[5:])
                cis.issuecomments.add(newcomment)
                return HttpResponse(u"评论提交成功！")
            except:
                return HttpResponse(u"远程服务器错误！请联系管理员")
        else:
            return HttpResponse(u"评论内容不能为空！")


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
                'hasEvent':hasNoEvent
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