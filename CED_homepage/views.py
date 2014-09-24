# -*- coding:utf-8 -*-
from django.shortcuts import render,render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import Http404
from CED_homepage.models import *
import json

#权限控制封装
def is_not_admin(view):
    def new_view(request,*args,**kwargs):
        try:
            CedEnvAdminGroup.objects.get(envadminname=request.user)
        except:
            return render_to_response("errorinfo.html",
                    {'errorinfo':u"你无权查看本页面"},
                ) #暂时处理
        else:
            return view(request,*args,**kwargs)
    return new_view


#登陆控制封装
def requirelogin(view):
    """包装login"""
    def new_view(request,*args,**kwargs):
        if request.user.is_authenticated():
            return view(request,*args,**kwargs)
        else:
            return HttpResponseRedirect("/login")
    return new_view


#CED首页
@requirelogin
def homepage(request):
    #获取所有issues
    allissues=ced_issues.objects.all()
    allevents=ced_events.objects.all()
    hasNoEvent=False
    ISADMIN = False

    # 专门为非管理员准备的数据
    isnotadminissues=ced_issues.objects.filter(issuesubman=request.user)

    try:
        CedEnvAdminGroup.objects.get(envadminname=request.user)
    except:
        ISADMIN=False
    else:
        ISADMIN=True

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
            'isadmin':ISADMIN,
            'isnotadminissues':isnotadminissues,
        }

    )

#用于工具的实时输出
@requirelogin
def redis_io_info(request):
    pass

#详情页处理
@requirelogin
def ced_issue_detail(request,cedis):
    hasNoEvent=False

    ISADMIN = False
    ISSUBMAN=False

    try:
        CedEnvAdminGroup.objects.get(envadminname=request.user)
    except:
        ISADMIN=False
    else:
        ISADMIN=True

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

    if cedisone.issuesubman.username == request.user.username:
        ISSUBMAN=True
    else:
        ISSUBMAN=False

    return render_to_response("cedisdetail.html",
        {
            "thiscedis":cedisone,
            'myevents':myevents[0:10],
            'myeventsnum':myeventsnum,
            'hasEvent':hasNoEvent,
            'curuser':request.user,
            'isadmin':ISADMIN,
            'issubman':ISSUBMAN,
        }
    )

#显示我的所有事件列表
@requirelogin
def ced_show_allmyevents(request):
    hasNoEvent=False

    ISADMIN = False

    try:
        CedEnvAdminGroup.objects.get(envadminname=request.user)
    except:
        ISADMIN=False
    else:
        ISADMIN=True

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
            'isadmin':ISADMIN,
    })

#Ajax推送评论消息
@requirelogin
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
@requirelogin
def show_cat_issues(request,cattype):

    hasNoEvent=False

    ISADMIN = False

    try:
        CedEnvAdminGroup.objects.get(envadminname=request.user)
    except:
        ISADMIN=False
    else:
        ISADMIN=True

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
                'isadmin':ISADMIN,

            }

        )
    except:
        return Http404()


#分类issue mine 显示，即只显示提交人为自己的单子
@requirelogin
def show_cat_issues_mine(request,cattype):

    hasNoEvent=False

    ISADMIN = False

    try:
        CedEnvAdminGroup.objects.get(envadminname=request.user)
    except:
        ISADMIN=False
    else:
        ISADMIN=True

    """分类显示"""
    try:
        u_issue_status=int(cattype)
        c_issues=ced_issues.objects.all().filter(issuestatus=u_issue_status,issuesubman=request.user)

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
                'isadmin':ISADMIN,

            }

        )
    except:
        return Http404()


#通知对方的实现,ajax
@requirelogin
@is_not_admin
def ced_ajax_notify(request,cedis):
    """通知对方"""
    thisissue_id=cedis[5:]
    thisissue=ced_issues.objects.get(id=thisissue_id) #定位该问题单
    thisissue_current_status=thisissue.issuestatus
    if request.method=="POST":
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



#通知对方已解决的ajax
@requirelogin
def ced_ajax_notify_done(request,cedis):
    """用于非管理员通知管理员已解决"""
    thisissue_id=cedis[5:]
    thisissue=ced_issues.objects.get(id=thisissue_id) #定位该问题单
    thisissue_current_status=thisissue.issuestatus
    if request.method=="POST" and thisissue.issuesubman.username == request.user.username:
        if thisissue_current_status==3 or thisissue_current_status==1 or thisissue_current_status==4:  # 新建单子不能随便关闭
            return HttpResponse(u"当前状态无需通知！")
        else:
            try:
                thisissue.issuestatus=3 #置为已解决
                thisissue.save() #保存并触发事件通知
            except:
                return HttpResponse(u"通知过程中发生异常")
            else:
                return HttpResponse(u"该问题单被成功关闭！")
    else:
        return HttpResponse(u"非法请求")


#用于非管理员驳回的ajax
@requirelogin
def ced_ajax_notify_bo(request,cedis):
    """用于非管理员驳回的ajax"""
    thisissue_id=cedis[5:]
    thisissue=ced_issues.objects.get(id=thisissue_id) #定位该问题单
    thisissue_current_status=thisissue.issuestatus

    if request.method=="POST" and thisissue.issuesubman.username == request.user.username:

        if thisissue_current_status==3 or thisissue_current_status==1 or thisissue_current_status==4: #  新建单子不能随便驳回
            return HttpResponse(u"当前状态无需通知！")
        else:
            try:
                thisissue.issuestatus=4 #置为驳回
                thisissue.save() #保存并触发事件通知
            except:
                return HttpResponse(u"通知过程中发生异常")
            else:
                return HttpResponse(u"成功驳回该单子！")
    else:
        return HttpResponse(u"非法请求")


#搜索直达功能
@requirelogin
def ced_search_issue(request):
    pass


#ajax定时拉取事件
@requirelogin
def ced_ajax_get_eventlists(request):
    """返回JSON数据,给前端解析"""
    if request.method=="POST":
        pass


#获取英雄榜列表
@requirelogin
def ced_get_hero_lists(request):

    hasNoEvent=False

    ISADMIN = False

    try:
        CedEnvAdminGroup.objects.get(envadminname=request.user)
    except:
        ISADMIN=False
    else:
        ISADMIN=True

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
            'isadmin':ISADMIN,

        }
    )


#数据展示页面
@requirelogin
def ced_show_alldatas(request):

    hasNoEvent=False

    ISADMIN = False

    try:
        CedEnvAdminGroup.objects.get(envadminname=request.user)
    except:
        ISADMIN=False
    else:
        ISADMIN=True

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
            'isadmin':ISADMIN,
        }
    )


#环境管理员个人设置页面
@requirelogin
@is_not_admin
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
@requirelogin
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
@requirelogin
def ced_ajax_new_issue_submit(request):

    hasNoEvent=False

    ISADMIN = False

    try:
        CedEnvAdminGroup.objects.get(envadminname=request.user)
    except:
        ISADMIN=False
    else:
        ISADMIN=True

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
            'isadmin':ISADMIN,

        }
    )

@requirelogin
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

            #提交DB之前先判断其是否有空,防止状态变更刷新不及时导致的问题
            thisadminusr=AuthUser.objects.get(username=request.POST["whoischoosed"])
            if CedEnvAdminGroup.objects.get(envadminname=thisadminusr).envadminstatus==0:
                newissue.issuereceivemans.add(thisadminusr)
            else:
                newissue.delete() #删除之前的newissue对象,不允许保存
                return render_to_response("errorinfo.html",
                        {'errorinfo':u"该管理员目前不可用！"},
                )

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

@requirelogin
def ced_ajax_save_commentfile(request):
    pass

@requirelogin
def ced_ajax_clear_all_notify(request):
    """消除所有的通知"""
    pass

def ced_ajax_all_issues_info(request):
    """公共接口，返回所有issues的信息,返回JSON"""
    istitles=[]
    allissues=ced_issues.objects.all()
    for iss in allissues:  # 用于判定是不是同一个issue
        istitles.append(
            {
                'isid':iss.id,
                'istitle':iss.issuetitle,
                'istype':iss.issuetypes.issuetype,
                'iskeys':[thiskey.keyname for thiskey in iss.issuekey.all()]
            }
        )

    return HttpResponse(json.dumps(istitles),content_type="application/json")


def ced_ajax_all_keys_info(request):
    """公共接口，返回所有在库的线索信息,返回JSON"""
    iskeys=[]
    allkeys=ced_keys.objects.all()
    for k in allkeys:  # 用于判定是不是同一个issue
        iskeys.append(k.keyname)
    return HttpResponse(json.dumps(iskeys),content_type="application/json")


@requirelogin
def ced_markall_readed(request):
    # 开始删除,保证删的是自己的事件单，并不影响单子本身
    for event in ced_events.objects.all():
        if len(event.user_r.all().filter(username=request.user.username)) != 0:
            try:
                event.delete()
            except:
                continue
    return HttpResponse("已全部标记为已读!")


def ced_help(request):
    """CED help"""
    pass