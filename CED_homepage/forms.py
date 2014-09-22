#!/usr/bin/env python
# -*- coding:utf-8 -*-

from django import forms
from ckeditor.widgets import CKEditorWidget

#评论页表单
class commentForm(forms.Form):
    #自定义widget,以修改text默认class
    commentcontent=forms.CharField(widget=CKEditorWidget(),required=True,label=u"")