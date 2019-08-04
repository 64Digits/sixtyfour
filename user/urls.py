
from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
	path('<username>', views.post_listing, name='index'),
	path('<username>/page/<int:page>', views.post_listing, name='listing'),
	path('<username>/post/<int:entry>', views.post_detail, name='post'),
	path('<username>/post/<int:entry>/page/<int:page>', views.post_detail, name='post'),
]
