from bbcode import Parser
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from urllib.parse import urlparse, parse_qs
import random
import re
from markdown import markdown
from .utils import static_var
from pygments.formatters import HtmlFormatter;
from pygments.lexers import get_lexer_by_name, guess_lexer;
from pygments import highlight;
from pygments.util import ClassNotFound

# BB64 Meta (Decorators)

def bb64_embed_responsive(fn):
	def wrapper_fn(tag_name, value, options, parent, context):
		inner=fn(tag_name, value, options, parent, context)
		return format_html('<div class="embed-responsive embed-responsive-16by9">{}</div>',inner)
	return wrapper_fn

def bb64_exempt_preview(placeholder=None):
	def decorator(fn):
		def wrapper_fn(tag_name, value, options, parent, context):
			if context and 'preview' in context and context['preview']:
				return placeholder if placeholder is not None else '[%s]'%tag_name
			return fn(tag_name, value, options, parent, context)
		return wrapper_fn
	return decorator

# BB64 Tags

def bb64_img(tag_name, value, options, parent, context):
	title = 'Image'
	width = ''
	height = ''

	if 'title' in options:
		title = options['title']
	if 'width' in options:
		width = options['width']
	if 'height' in options:
		height = options['height']

	return format_html('<img class="bbcode-img" src="{value}" title="{title}" width="{width}" height="{height}">',
		value=value, title=title, width=width, height=height
	)

def bb64_rev(tag_name, value, options, parent, context):
	return format_html('<span class="bbcode-rev">{value}</span>', value=value[::-1])

def bb64_font(tag_name, value, options, parent, context):
	font = 'sans serif'
	if 'font' in options:
		font = options['font']
	return format_html('<span style="font-family: {font};">{value}</span>', font=font, value=mark_safe(value))

def bb64_size(tag_name, value, options, parent, context):
	size = ''
	if 'size' in options:
		size = re.sub(r"\D", "", options['size'])
	return format_html('<span style="font-size: {size}pt;">{value}</span>', size=size, value=mark_safe(value))

def bb64_color(tag_name, value, options, parent, context):
	if tag_name in options:
		color = options[tag_name].strip()
	elif options:
		color = list(options.keys())[0].strip()
	else:
		return value
	match = re.match(r'^([a-z]+)|^(#[a-f0-9]{3,6})', color, re.I)
	color = match.group() if match else 'inherit'
	return format_html('<span style="color:{color};">{value}</span>', color=color, value=mark_safe(value))

def bb64_tnail(tag_name, value, options, parent, context):
	width = '204'
	height = ''
	gallery_id = 'gallery'
	title = 'Image thumbnail'
	if 'width' in options:
		width = options['width']
	if 'height' in options:
		height = options['height']
	if 'gallery' in options:
		gallery_id = options['gallery']
	if 'title' in options:
		title = options['title']

	return format_html("""
		<a data-fancybox="{gallery_id}" href="{value}">
			<img title="{title}" src="{value}" width="{width}" height="{height}">
		</a>
	""",
		gallery_id=gallery_id, title=title, value=value, width=width, height=height
	)

def bb64_shh(tag_name, value, options, parent, context):
	current_user = context['request'].user
	if not current_user:
		return ""

	target_user = ''
	if 'shh' in options:
		target_user = options['shh']

	if current_user.is_authenticated and current_user.username == target_user:
		return format_html("""
		<div class="card">
			<div class="card-header">
				Whispering to {target_user}
			</div>

			<div class="card-body">
				{value}
			</div>
		</div>
		""", target_user=target_user, value=mark_safe(value))
	elif not current_user.is_authenticated and target_user == 'guest':
		return format_html("""
		<div class="card">
			<div class="card-header">
				Whispering to guest
			</div>

			<div class="card-body">
				{value}
			</div>
		</div>
		""", value=mark_safe(value))
	else:
		return ""

def bb64_blind(tag_name, value, options, parent, context):
	current_user = context['request'].user
	if not current_user:
		return ""

	target_user = ''
	if 'blind' in options:
		target_user = options['blind']

	if current_user.is_authenticated and current_user.username != target_user:
		return format_html("""
		<div class="card">
			<div class="card-header">
				Hiding from {target_user}
			</div>

			<div class="card-body">
				{value}
			</div>
		</div>
		""", target_user=target_user, value=mark_safe(value))
	else:
		return ""

def bb64_quote(tag_name, value, options, parent, context):
	target_user = options['quote'] if (options and 'quote' in options) else ''

	return format_html("""
	<div class="card">
		<div class="card-header">
			Quote: {target_user}
		</div>

		<div class="card-body">
			{value}
		</div>
	</div>
	""", target_user=target_user, value=mark_safe(value))

@static_var(hide_index = 0)
def bb64_hide(primary_reason, show=False, is_nsfw=False):
	@bb64_exempt_preview("")
	def bb64_hide_internal(tag_name, value, options, parent, context):
		reason = primary_reason
		if tag_name in options:
			reason = primary_reason + options[tag_name]

		bb64_hide.hide_index += 1

		params = {
			'header_class':'bg-danger' if is_nsfw else '',
			'button_class':'text-white' if is_nsfw else 'text-primary',
			'show_class':'show' if show else '',
			'reason':reason,
			'hide_id':"bbcode-hide-%d" % (bb64_hide.hide_index),
			'value':mark_safe(value)
		}

		return format_html("""
			<div class="card">
				<div class="card-header {header_class}">
					<button class="btn btn-link {button_class}" data-toggle="collapse" data-target="#{hide_id}">
						{reason}
					</button>
				</div>
				
				<div id="{hide_id}" class="collapse {show_class}">
					<div class="card-body">
						{value}
					</div>
				</div>
			</div>
		""", **params )
	return bb64_hide_internal

def bb64_user(tag_name, value, options, parent, context):
	user = value if value else ''
	return format_html('<a href="/user/{user}">{user}</a>', user=user)

def bb64_profile(tag_name, value, options, parent, context):
	user = ''
	if 'profile' in options:
		user = options['profile']
	
	return format_html('<a href="/user/{user}">{user}</a>', user=user)

def bb64_rand(tag_name, value, options, parent, context):
	choices = re.split(r"\[[oO0*@+x#|]\]", value)
	return choices[random.randint(0, len(choices)-1)]

def bb64_markdown(tag_name, value, options, parent, context):
	return markdown(value)

def bb64_theusertag(tag_name, value, options, parent, context):
	current_user = context['request'].user
	if current_user.is_authenticated:
		return current_user.username
	else:
		return 'guest'

@bb64_exempt_preview("(Embedded Audio)")
def bb64_h5audio(tag_name, value, options, parent, context):
	return format_html('<audio src={value} controls preload="none">Audio not supported</audio>', value=value)

@bb64_exempt_preview("(Embedded Video)")
def bb64_h5video(tag_name, value, options, parent, context):
	return format_html('<video src={value} controls>Video not supported</video>', value=value)

def get_yt_video_id(url):
	if not re.match('[\./]',url):
		return url
	if url.startswith(('youtu', 'www')):
		url = 'http://' + url
	query = urlparse(url)
	if 'youtube' in query.hostname:
		if query.path == '/watch':
			return parse_qs(query.query)['v'][0]
		elif query.path.startswith(('/embed/', '/v/')):
			return query.path.split('/')[2]
	elif 'youtu.be' in query.hostname:
		return query.path[1:]
	else:
		return ValueError

@bb64_exempt_preview("(Embedded Video)")
@bb64_embed_responsive
def bb64_youtube(tag_name, value, options, parent, context):
	video_id = get_yt_video_id(value)

	return format_html("""
		<iframe width="640" height="360" 
				class="bbcode-youtube" 
				src="https://www.youtube.com/embed/{video_id}" 
				frameborder="0"
				allow="encrypted-media;picture-in-picture" allowfullscreen></iframe>
	""", video_id=video_id)

@bb64_exempt_preview("(Embedded Video)")
@bb64_embed_responsive
def bb64_vimeo(tag_name, value, options, parent, context):
	video_id = value.split("/")[-1]

	return format_html("""
		<iframe src="https://player.vimeo.com/video/{video_id}" 
			width="640" 
			height="360" 
			frameborder="0" 
			allow="fullscreen" allowfullscreen></iframe>
	""", video_id=video_id)

@bb64_exempt_preview("(Embedded Audio)")
def bb64_soundcloud(tag_name, value, options, parent, context):
	return format_html("""
		<iframe 
			width="100%" height="300" 
			scrolling="no" 
			frameborder="no" 
			src="https://w.soundcloud.com/player/?url={value}"></iframe>
	""", value=value)

@bb64_exempt_preview("(Embedded Security Risk)")
@bb64_exempt_preview
def bb64_flash(tag_name, value, options, parent, context):
	width = '640'
	height = '360'
	if 'width' in options:
		width = options['width']
	if 'height' in options:
		height = options['height']
	return format_html("""
		<object type="application/x-shockwave-flash" 
			data="{value}" 
			width="{width}" height="{height}">
			<param name="movie" value="{value}" />
			<param name="quality" value="high"/>
		</object>
	""", width=width, height=height, value=value)

@bb64_exempt_preview()
def bb64_paypal(tag_name, value, options, parent, context):
	paypal_button_id = value.split("/")[-1]
	return format_html("""
		<form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_top">
			<input type="hidden" name="cmd" value="_s-xclick" />
			<input type="hidden" name="hosted_button_id" value="{paypal_button_id}" />
			<input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" border="0" name="submit" title="PayPal - The safer, easier way to pay online!" alt="Donate with PayPal button" />
		</form>""", paypal_button_id=paypal_button_id)

def bb64_code(tag_name, value, options, parent, context):
	lang = 'text'

	if tag_name in options:
		lang = options[tag_name]

	lexer = None
	try:
		lexer = get_lexer_by_name(lang)
	except ClassNotFound:
		try:
			lexer = guess_lexer(value)
		except ClassNotFound:
			lexer = get_lexer_by_name('text')
			
	formatter = HtmlFormatter(linenos=False)
	result = highlight(value, lexer, formatter)
	return format_html("""<div class="bbcode-code">{result}</div>""", result=mark_safe(mark_safe(result)))

def ExtendedParser():
	parser = Parser()

	simple=[
		'b','i','u','em', 'tt',
		'sub', 'sup', 'ul','ol','li',
		'h1','h2','h3','h4','h5','h6'
	]
	for t in simple:
		parser.add_simple_formatter(t, '<'+t+'>%(value)s</'+t+'>')

	parser.add_simple_formatter('right', '<span class="bbcode-right">%(value)s</span>', transform_newlines=False)
	parser.add_simple_formatter('flex', '<div class="bbcode-flex">%(value)s</div>')
  
	def bind(*args,**kwargs):
		parser.add_formatter(*args, **kwargs)

	bind('img', bb64_img, replace_links=False)
	bind('quote', bb64_quote, swallow_trailing_newline=True)
	bind('code', bb64_code, render_embedded escape_html=False)
	bind('rev', bb64_rev)
	bind('font', bb64_font)
	bind('size', bb64_size)
	bind('color', bb64_color)
	bind('tnail', bb64_tnail, replace_links=False)
	bind('hide', bb64_hide("Hide: "), swallow_trailing_newline=True)
	bind('show', bb64_hide("Hide: ", show=True), swallow_trailing_newline=True)
	bind('nsfw', bb64_hide("NSFW: ", is_nsfw=True), swallow_trailing_newline=True)
	bind('shh', bb64_shh, swallow_trailing_newline=True)
	bind('blind', bb64_blind, swallow_trailing_newline=True)
	bind('user', bb64_user)
	bind('profile', bb64_profile, standalone=True)
	bind('h5audio', bb64_h5audio, replace_links=False)
	bind('h5video', bb64_h5video, replace_links=False)
	bind('audio', bb64_h5audio, replace_links=False)
	bind('youtube', bb64_youtube, replace_links=False)
	bind('youtubehd', bb64_youtube, replace_links=False)
	bind('youtubeaudio', bb64_youtube, replace_links=False)
	bind('vimeo', bb64_vimeo, replace_links=False)
	bind('soundcloud', bb64_soundcloud, replace_links=False)
	#bind('flash', bb64_flash, replace_links=False) # Too risky
	bind('paypal', bb64_paypal, replace_links=False)
	bind('theusertag', bb64_theusertag, standalone=True)
	bind('rand', bb64_rand)
	bind('markdown', bb64_markdown, render_embedded=False)

	aliases = {
		'ln': 'hr',
		'col': 'color',
		'colour': 'color',
		'md': 'markdown',
		'choice': 'rand',
	}

	for k,v in aliases.items():
		parser.recognized_tags[k] = parser.recognized_tags[v]

	return parser

main_parser = ExtendedParser()
def bbcode64(entry, context=None):
	context['parser_obj'] = entry
	processed = main_parser.format(entry.entry.strip(), **context)
	return format_html('<div class="bbcode"><p>{}</p></div>',mark_safe(processed))

