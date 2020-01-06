
from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
	path('<username>', views.UserPostListView.as_view(), name='listing'),
	path('<username>/page/<int:page>', views.UserPostListView.as_view(), name='listing'),
	path('<username>/post/<int:entry>', views.PostCommentListView.as_view(), name='post'),
	path('<username>/post/<int:entry>/page/<int:page>', views.PostCommentListView.as_view(), name='post'),
	path('<username>/post/<int:pk>/edit', views.PostUpdate.as_view(), name='post_edit'),
	path('comment/<int:pk>/edit', views.CommentUpdate.as_view(), name='comment_edit'),
	path('<username>/post/<int:pk>/delete', views.PostDelete.as_view(), name='post_delete'),
	path('comment/<int:pk>/delete', views.CommentDelete.as_view(), name='comment_delete'),
]
