"""sixtyfour URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings

from django.contrib.auth import views as auth_views
from user.views import FrontListView, NewsListView, PostCreate

sixtyfour = ([
	path('', FrontListView.as_view(), name='front'),
	path('page/<int:page>', FrontListView.as_view(), name='front'),
	path('news', NewsListView.as_view(), name='news'),
	path('news/page/<int:page>', NewsListView.as_view(), name='news'),
	path('login', auth_views.LoginView.as_view(), name='login'),
	path('logout', auth_views.LogoutView.as_view(), name='logout'),
	path('submit', PostCreate.as_view(), name='submit'),
], 'sixtyfour')

urlpatterns = [
	path('', include(sixtyfour)),
	path('admin/', admin.site.urls),
	path('user/', include('user.urls')),
] 

if settings.DEBUG:
	urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
