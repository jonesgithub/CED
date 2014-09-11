#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.db import models
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.dispatch import receiver

#导入的模型-用户
class AuthUser(models.Model):
    id = models.IntegerField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField()
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=75)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    def __unicode__(self):
        return self.username

    class Meta:
        managed = False
        db_table = 'auth_user'

#issue标签模型
class ced_types(models.Model):
    issuetype=models.CharField(max_length=50,primary_key=True)

    def __unicode__(self):
        return self.issuetype

#issue线索模型
class ced_keys(models.Model):
    keyname=models.TextField()

    def __unicode__(self):
        return self.keyname

class ced_issue_comments(models.Model):
    commentman=models.ForeignKey(AuthUser)
    comment=models.TextField()
    commentdate=models.DateTimeField(auto_now=True)
    events = generic.GenericRelation('ced_events') #关联事件模型

    def __unicode__(self):
        return self.comment

    @property
    def commentcontent(self):
        return self.commentman+"说："+self.comment

#issue详情模型
class ced_issues(models.Model):
    """
    issuestatus:1 新建(默认) 2 等待确认 3 关闭 4 驳回状态
    """
    issuetitle=models.CharField(max_length=50)
    issuedetail=models.TextField()
    issuetypes=models.ForeignKey(ced_types)
    issuekey=models.ManyToManyField(ced_keys,blank=True) #可以不提供线索
    issuesubman=models.ForeignKey(AuthUser,related_name="subman")
    issuecreatetime=models.DateTimeField(auto_now=True,blank=True)
    issuestatus=models.IntegerField(default=1)
    issuecomments=models.ManyToManyField(ced_issue_comments,blank=True) #添加评论记录
    issuereceivemans=models.ManyToManyField(AuthUser,related_name="recman") #事件处理者,委托接受人
    events = generic.GenericRelation('ced_events') #关联事件模型

    @property
    def issueid(self):
        return "cedis"+str(self.id)

    @property
    def issuedetailurl(self):
        return "/cedis/"+self.issueid+"/detail/"

    @property
    def issuestatusname(self):
        if self.issuestatus==1:
            return u"未解决"
        elif self.issuestatus==2:
            return u"待确认"
        elif self.issuestatus==3:
            return u"已解决"
        elif self.issuestatus==4:
            return u"被驳回"

    class Meta:
        ordering=['-issuecreatetime']

    def __unicode__(self):
        return self.issuetitle

#存放事件和消息通知的模型
class ced_events(models.Model):
    user_s=models.ForeignKey(AuthUser,related_name="user_s")
    user_r=models.ManyToManyField(AuthUser,related_name="user_r")
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    event_object = generic.GenericForeignKey('content_type', 'object_id')
    eventdes=models.TextField() #描述这条事件
    eventstatus=models.IntegerField(default=0) #0表示未读事件
    eventdatetime=models.DateTimeField(auto_now=True) #事件发生的事件

    def __unicode__(self):
        return self.eventdes

    @property
    def isUnread(self):
        if self.eventstatus==0:
            return True
        elif self.eventstatus==1:
            return False

    class Meta:
        ordering=['-eventdatetime']

#注册监听issues通知事件
@receiver(post_save,sender=ced_issues,dispatch_uid="ced_issue_update")
def _cedissue_event_handle(sender,instance,**kwargs):
    """根据单子状态决定通知行为"""
    thisissue=instance #实例化发送者
    if thisissue.issuestatusname==u'待确认': #如果是待确认,由问题单处理人发送给subman
        thisevent=ced_events(
            user_s=thisissue.issuereceivemans.all()[0], #只允许选择一个环境处理人/永远为当前那个
            event_object=thisissue,
            eventdes=(u"<a href='%s' title='查看问题单详情' target='_blank'>【%s】解决了问题单【%s】，请及时反馈！</a>" %
                  (thisissue.issuedetailurl,thisissue.issuereceivemans.all()[0],thisissue.issuetitle[:10]+u"......")
            )
        )
        thisevent.save() #保存这条事件,顺序在前
        #加入事件收取人
        #for revman in thisissue.issuereceivemans.all():
            #thisevent.user_r.add(revman)
        thisevent.user_r.add(thisissue.issuesubman) #事件收取人为问题提交人

    elif thisissue.issuestatusname==u'已解决':
        thisevent=ced_events(
            user_s=thisissue.issuesubman,
            event_object=thisissue,
            eventdes=(u"<a href='%s' title='查看问题单详情' target='_blank'>【%s】确认了问题单【%s】已解决！</a>" %
                  (thisissue.issuedetailurl,thisissue.issuesubman,thisissue.issuetitle[:10]+u"......")
            )
        )
        thisevent.save() #保存这条事件,顺序在前
        #加入事件收取人
        for revman in thisissue.issuereceivemans.all():
            thisevent.user_r.add(revman)

    elif thisissue.issuestatusname==u'被驳回':
        thisevent=ced_events(
            user_s=thisissue.issuesubman,
            event_object=thisissue,
            eventdes=(u"<a href='%s' title='查看问题单详情' target='_blank'>【%s】驳回了问题单【%s】，请尝试再次解决！</a>" %
                  (thisissue.issuedetailurl,thisissue.issuesubman,thisissue.issuetitle[:10]+u"......")
            )
        )
        thisevent.save() #保存这条事件,顺序在前
        #加入事件收取人
        for revman in thisissue.issuereceivemans.all():
            thisevent.user_r.add(revman)

    else:
        #新建状态直接写事件
        thisevent=ced_events(
            user_s=thisissue.issuesubman,
            event_object=thisissue,
            eventdes=(u"<a href='%s' title='查看问题单详情' target='_blank'>【%s】提交了一个新的问题单【%s】！</a>" %
                  (thisissue.issuedetailurl,thisissue.issuesubman,thisissue.issuetitle[:10]+u"......")
            )
        )
        thisevent.save() #保存这条事件,顺序在前
        #加入事件收取人
        for revman in thisissue.issuereceivemans.all():
            thisevent.user_r.add(revman)
