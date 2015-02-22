from django.conf.urls import patterns, include, url
from django.contrib import admin

from dimib import views


urlpatterns = patterns('',
    url(r'^api/auth/login/', views.ApiAuth.as_view({'post': 'login'}), name = 'login'),
    url(r'^api/auth/logout/', views.ApiAuth.as_view({'get': 'logout'}), name = 'logout'),
    url(r'^api/auth/', views.ApiAuth.as_view({'get': 'get_user'}), name = 'auth'),
    url(r'^api/post/(?P<post_id>\d+)/comments/', views.ApiPost.as_view({'get': 'get_comments', 'post': 'add_comment'}), name = 'comments'),
    url(r'^api/post/(?P<post_id>\d+)/', views.ApiPost.as_view({'get': 'get_post'}), name = 'post'),
    url(r'^api/post/', views.ApiPost.as_view({'get': 'get_posts', 'post': 'add_post'}), name = 'posts'),
    url(r'^api/registration/', views.ApiAuth.as_view({'post': 'registrate'}), name = 'registration'),
    url(r'^admin/', include(admin.site.urls)),
)
