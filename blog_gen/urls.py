from django.urls import path
from .views import *


urlpatterns = [
    path('', index, name='index'),
    path('login', login, name='login'),
    path('signup', signup, name='signup'),
    path('logout', logout, name='logout'),
    path('home', home, name='home'),
    path('initialize', initialize, name='initialize'),
    path('home/<str:id>', show_blog, name='blog'),
    path('home/<str:id>/<str:action>', blog_action, name='blog_action'),
    path('add_blog', add_blog, name='add_blog'),
    path('all_blogs', all_blogs, name='all_blogs'),
    path('liked_blogs', liked_blogs, name='liked_blogs'),
]
