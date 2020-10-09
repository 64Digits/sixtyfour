
from django.urls import path, include
from . import views

from django.views.generic.base import TemplateView
from django_registration.backends.activation import views as reg_views
from .forms import RegistrationForm
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'recent_activity', views.RecentActivityList, basename='recent')

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
	path('api/recent_activity/get', views.RecentActivityList.as_view({'get':'list'}), name="recent_activity")
]

regpatterns = [
	path("activate/complete",
		TemplateView.as_view(template_name="django_registration/activation_complete.html"),
		name="django_registration_activation_complete",
	),
	path("activate/<str:activation_key>",
		reg_views.ActivationView.as_view(),
		name="django_registration_activate",
	),
	path("register",
		reg_views.RegistrationView.as_view(form_class=RegistrationForm),
		name="django_registration_register",
	),
	path("register/complete",
		TemplateView.as_view(template_name="django_registration/registration_complete.html"),
		name="django_registration_complete",
	),
	path("register/closed",
		TemplateView.as_view(template_name="django_registration/registration_closed.html"),
		name="django_registration_disallowed",
	),
]
