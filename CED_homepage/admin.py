from django.contrib import admin
from CED_homepage.models import *

# Register your models here.
admin.site.register(ced_issues)
admin.site.register(ced_keys)
admin.site.register(ced_types)
admin.site.register(ced_issue_comments)
admin.site.register(ced_events)
admin.site.register(CedEnvAdminGroup)