from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.template.defaultfilters import truncatewords_html

from sixtyfour.formatters import bbcode64
from sixtyfour.filetypes import get_filetype, get_fileicon
from sixtyfour.utils import ObjectView

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
def user(user, display=None):
	if not display:
		display = user.username
	return format_html('<a href="{}">{}</a>',mark_safe(user.profile.url),display)

@register.simple_tag
def user_avatar(user, link=True):
	if link:
		args = [user.profile.url, user.username]
		tpl = '<a href="{}"><img title="{}" class="avatar" src="{}"/></a>'
	else:
		args = [user.username]
		tpl = '<img title="{}" class="avatar" src="{}"/>'

	if hasattr(user, 'profile') and user.profile.avatar:
		args += [user.profile.avatar_url]
	else:
		args += ['/static/images/default_avatar.png']

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

@register.simple_tag(takes_context=True)
def formatted_simple(context, content):
	ctx = {}
	[ctx.update(c) for c in context.dicts]
	res = bbcode64(ObjectView({'entry':content}), ctx)
	return res

@register.simple_tag()
def file_icon(url):
	return get_fileicon(url)

@register.inclusion_tag('include/filepreview.html')
def file_preview(name,url):
	filetype = get_filetype(url)
	return {
		'name': name,
		'url': url,
		'type': filetype,
	}
