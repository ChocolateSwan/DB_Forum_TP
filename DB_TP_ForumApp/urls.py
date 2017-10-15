"""DB_TP_ForumApp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from application.views import create_forum, details_forum, \
    create_thread, create_user, profile_user, threads_forum, \
    clear_service, create_post, status_service, create_vote, \
    forum_users,thread_details, thread_posts, post_details

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'forum/create', create_forum),
    url(r'forum/(?P<slug>[\w-]+)/details', details_forum),
    url(r'forum/(?P<slug>[\w-]+)/create', create_thread),
    url(r'user/(?P<nickname>[.\w-]+)/create', create_user),
    url(r'user/(?P<nickname>[.\w-]+)/profile', profile_user),
    url(r'forum/(?P<slug>[.\w-]+)/threads', threads_forum),
    url(r'service/clear', clear_service),
    url(r'thread/(?P<slug_or_id>[.\w\d-]+)/create', create_post),
    url(r'service/status', status_service),
    url(r'thread/(?P<slug_or_id>[.\w\d-]+)/vote', create_vote),
    url(r'forum/(?P<slug>[.\w-]+)/users', forum_users),
    url(r'thread/(?P<slug_or_id>[.\w\d-]+)/details', thread_details),
    url(r'thread/(?P<slug_or_id>[.\w\d-]+)/posts', thread_posts),
    url(r'post/(?P<id>[\d]+)/details', post_details),






]
