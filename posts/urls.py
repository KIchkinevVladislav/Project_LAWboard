from django.urls import path


from . import views

urlpatterns = [
    path('500/', views.server_error, name='server_error'), 
    path('404/', views.page_not_found, name='page_not_found'),
    path('', views.index, name='index'),
    path('new/', views.new_post, name='new_post'),
    path('group/<slug:slug>/', views.group_posts, name='group'),
    path('follow/', views.follow_index, name='follow_index'),
    path('<str:username>/follow/', views.profile_follow, name='profile_follow'), 
    path('<str:username>/unfollow/', views.profile_unfollow, name='profile_unfollow'),
    path('<str:username>/<int:post_id>/', views.post, name='post'),
    path(
        '<str:username>/<int:post_id>/edit/', 
        views.post_edit, 
        name='post_edit'
    ),
    path('<username>/<int:post_id>/comment', views.add_comment, name='add_comment'),
    path('<str:username>/', views.profile, name='profile'),    
]

    
    