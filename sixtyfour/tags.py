from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.html import format_html

from django import template
register = template.Library()

@register.inclusion_tag('include/pagination.html', takes_context=True)
def pagination(context, page, view, *args, **kwargs):
	#view = kwargs['view']
	context['view'] = view
	#kwargs.pop('view', None)
	
	#page = kwargs['page']
	context['page'] = page
	#kwargs.pop('page', None)
	
	if page.has_previous():
		context['page_first'] = reverse(view, kwargs=kwargs)
		kwargs['page'] = page.previous_page_number()
		context['page_previous'] = reverse(view, kwargs=kwargs)
	
	if page.has_next():
		kwargs['page'] = page.next_page_number()
		context['page_next'] = reverse(view, kwargs=kwargs)
		kwargs['page'] = page.paginator.num_pages
		context['page_last'] = reverse(view, kwargs=kwargs)

	return context

@register.simple_tag
def user(user):
	url=reverse('user:listing', kwargs={'username':user.username})
	return format_html('<a href="{}">{}</a>',mark_safe(url),user.username)
	
