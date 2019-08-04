
from django.urls import path
from . import views

urlpatterns = [
	path('<username>', views.post_listing, name='user'),
	path('<username>/page/<int:page>', views.post_listing, name='user-listing'),
	path('<username>/post/<int:entry>', views.post_detail, name='user-post'),
]
