from django.urls import path
from .views import InfoPageView

urlpatterns = [
	path('<slug:slug>', InfoPageView.as_view(), name='page'),
]
