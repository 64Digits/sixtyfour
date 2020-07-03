from django.conf import settings

from .models import LinkList

def get_linklists(request):
	res = LinkList.objects.all()
	lut = {}
	for ll in res:
		lut.update({ll.key:ll.link_set.filter(published=True).order_by('sort').all()})
	return {
		'link_list':lut,
	}

all_processors = [
	get_linklists,
]

def all(request):
	combined = {}
	for f in all_processors:
		combined.update(f(request))
	return combined
