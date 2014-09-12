from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()
from CED_homepage import views
from codesync import views as codesync_views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'CED.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$',views.homepage), #homepageview
    url(r'^cedis/(?P<cedis>\w+)/detail/$',views.ced_issue_detail),
    url(r'^allmyevents/$',views.ced_show_allmyevents),
    url(r'^ckeditor/', include('ckeditor.urls')),
    url(r'^cedis/(?P<cedis>\w+)/detail/addnewcomment/$',views.ced_ajax_addnewcomment),
    url(r'^cedis/(?P<cedis>\w+)/detail/notifysubman/$',views.ced_ajax_notify), #notity the subman
    url(r'^categories/(\d+)$',views.show_cat_issues),
    url(r'^geteventlists/$',views.ced_ajax_get_eventlists),
    url(r'^cedheros/$',views.ced_get_hero_lists),
    url(r'^showdatas/$',views.ced_show_alldatas),
    url(r'^myconfig/$',views.ced_person_config),

    #AI
    url(r'^tools/codesync/$',codesync_views.codesync_home_page),
    url(r'^tools/codesync/ajaxgetdomainconfig/(.+)',codesync_views.ajax_get_domainconfig),
    url(r'^tools/codesync/ajaxgetenvdetail/(.+)',codesync_views.ajax_get_env_detail),
    url(r'^tools/codesync/ajaxgetsyncprocess/',codesync_views.ajax_get_xmlrpc_run_info),

    #Single Sync
    url(r'^tools/codesync/ajaxstartsgsync/',codesync_views.single_site_sync),
)