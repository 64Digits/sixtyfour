from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.template.defaultfilters import truncatewords_html

from sixtyfour.formatters import bbcode64

from django import template
register = template.Library()

@register.inclusion_tag('include/pagination.html', takes_context=True)
def pagination(context, *args, **kwargs):
	if context['is_paginated']:
		page = context['page_obj']
		view = context['request'].resolver_match.view_name	
		kwargs = context['request'].resolver_match.kwargs

		if page.has_previous():
			kwargs.pop('page', None)
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

@register.simple_tag
def user_avatar(user):
	tpl='<img title="{}" class="avatar" src="{}"/>'

	if hasattr(user, 'profile'):
		args=[user.username + "'s avatar", user.profile.avatar]
	else:
		args=['Default avatar', '/static/images/default_avatar.png']

	return format_html(tpl, *args)

@register.simple_tag(takes_context=True)
def formatted(context, post=None, truncate=None):
	if not post:
		post = context['post']
	ctx = {'preview':True} if truncate else {}
	[ctx.update(c) for c in context.dicts]
	res = bbcode64(post, ctx)
	if truncate:
		return truncatewords_html(res, truncate)
	else:
		return res
