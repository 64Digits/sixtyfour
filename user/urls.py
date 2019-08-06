
from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
	path('<username>', views.UserPostListView.as_view(), name='listing'),
	path('<username>/page/<int:page>', views.UserPostListView.as_view(), name='listing'),
	path('<username>/post/<int:entry>', views.PostCommentListView.as_view(), name='post'),
	path('<username>/post/<int:entry>/page/<int:page>', views.PostCommentListView.as_view(), name='post'),
]
