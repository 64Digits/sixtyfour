from django.conf import settings

def site_branding(request):
	return {
		'site_name': settings.SITE_NAME,
	}

def sidebars(request):
	return {
		'sidebars': []
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
