from django.conf import settings
from user.views import LoginBar, LoggedInBar, RecentActivityBar

def site_branding(request):
	return {
		'site_name': settings.SITE_NAME,
		'site_logo': settings.SITE_LOGO if hasattr(settings, 'SITE_LOGO') else None,
	}

def sidebars(request):
	global_sidebar = []
	if request.user.is_authenticated:
		global_sidebar.append(LoggedInBar())
	else:
		if request.resolver_match.view_name != 'sixtyfour:login':
			global_sidebar.append(LoginBar())
	
	# Add in the Recent Activity widget here
	global_sidebar.append(RecentActivityBar())

	return {
		'global_sidebar': global_sidebar
	}

all_processors = [
	site_branding,
	sidebars,
]

def all(request):
	combined = {}
	for f in all_processors:
		combined.update(f(request))
	return combined
