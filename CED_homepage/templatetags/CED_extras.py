# -*- coding:utf-8 -*-
from django import template
from CED_homepage.models import *

#过滤器注册全局定义
register=template.Library()

#过滤nav头像

#过滤用户名真实姓名
@register.filter(name='getUsername')
def getUsername(alias):
    try:
        myusername=UserInfo.objects.using('reportplatform').get(useralias=alias).username
    except UserInfo.DoesNotExist:
        myusername=AuthUser.objects.using('default').get(username=alias).username
    return myusername
