
from django.conf import settings

def site_branding(request):
	include_settings = {
		'site_name': settings.SITE_NAME,
	}

	return include_settings
