from django.conf import settings

def site_branding(request):
	return {
		'site_name': settings.SITE_NAME,
		'site_logo': settings.SITE_LOGO if hasattr(settings, 'SITE_LOGO') else None,
	}

def sidebars(request):
	return {
		'global_sidebar': []
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
