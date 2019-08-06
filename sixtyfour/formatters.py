from bbcode import Parser
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from urllib.parse import urlparse, parse_qs
import random
import re
from markdown import markdown
from .utils import static_var

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

	return f'<img class="bbcode-img" src="{value}" title="{title}" width="{width}" height="{height}" >'

def bb64_rev(tag_name, value, options, parent, context):
	return f'<span class="bbcode-rev">{value[::-1]}</span>'

def bb64_font(tag_name, value, options, parent, context):
	font = 'sans serif'
	if 'font' in options:
		font = options['font']
	return f'<span style="font-family: {font};">{value}</span>'

def bb64_size(tag_name, value, options, parent, context):
	size = ''
	if 'size' in options:
		size = re.sub(r"\D", "", options['size'])
	return f'<span style="font-size: {size}pt;">{value}</span>'

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

	return f"""
		<a data-fancybox="{gallery_id}" href="{value}">
			<img title="{title}" src="{value}" width="{width}" height="{height}">
		</a>
	"""

def bb64_shh(current_user):
	def bb64_shh_internal(tag_name, value, options, parent, context):
		target_user = ''
		if 'shh' in options:
			target_user = options['shh']

		if not current_user:
			return ""

		if current_user.is_authenticated and current_user.username == target_user:
			return f"""
				<div class="card">
				<div class="card-header">
					<h5 class="mb-0">
						Whispering to {target_user}
					</h5>
				</div>

				<div class="card-body">
					{value}
				</div>
			</div>
			"""
		elif not current_user.is_authenticated and target_user == 'guest':
			return f"""
				<div class="card">
				<div class="card-header">
					<h5 class="mb-0">
						Whispering to guest
					</h5>
				</div>

				<div class="card-body">
					{value}
				</div>
			</div>
			"""
		else:
			return ""
	return bb64_shh_internal

def bb64_blind(current_user):
	def bb64_blind_internal(tag_name, value, options, parent, context):
		target_user = ''

		if not current_user:
			return ""

		if 'blind' in options:
			target_user = options['blind']

		if current_user.is_authenticated and current_user.username != target_user:
			return f"""
				<div class="card">
				<div class="card-header">
					<h5 class="mb-0">
						Hiding from {target_user}
					</h5>
				</div>

				<div class="card-body">
					{value}
				</div>
			</div>
			"""
		else:
			return ""
	return bb64_blind_internal


@static_var(hide_index = 0)
def bb64_hide(primary_reason, show=False, is_nsfw=False):
	def bb64_hide_internal(tag_name, value, options, parent, context):
		reason = primary_reason
		if tag_name in options:
			reason = primary_reason + options[tag_name]
		
		hide_id = "bbcode-hide-%d" % (bb64_hide.hide_index)
		bb64_hide.hide_index += 1

		return f"""
			<div class="card">
				<div class="card-header {'bg-danger' if is_nsfw else 'text-primary'}">
					<h5 class="mb-0">
						<button class="btn btn-link {'text-white' if is_nsfw else 'text-info'}" data-toggle="collapse" data-target="#{hide_id}">
							{reason}
						</button>
					</h5>
				</div>
				
				<div id="{hide_id}" class="collapse {'show' if show else ''}">
					<div class="card-body">
						{value}
					</div>
				</div>
			</div>
		"""
	return bb64_hide_internal

def bb64_profile(tag_name, value, options, parent, context):
	user = ''
	if 'profile' in options:
		user = options['profile']
	
	return f'<a href="/user/{user}">{user}</a>'

def bb64_h5audio(tag_name, value, options, parent, context):
	return f'<audio src={value} controls preload="none">Audio not supported</audio>'

def bb64_h5video(tag_name, value, options, parent, context):
	return f'<video src={value} controls>Video not supported</video>'

def bb64_youtube(tag_name, value, options, parent, context):
	url = urlparse(value)
	data = parse_qs(url.query)
	video_id = data['v'][0]

	return f"""
		<iframe width="640" height="360" 
				class="bbcode-youtube" 
				src="https://www.youtube.com/embed/{video_id}" 
				frameborder="0"
				allow="encrypted-media;picture-in-picture" allowfullscreen></iframe>
	"""

def bb64_vimeo(tag_name, value, options, parent, context):
	video_id = value.split("/")[-1]

	return f"""
		<iframe src="https://player.vimeo.com/video/{video_id}" 
			width="640" 
			height="360" 
			frameborder="0" 
			allow="fullscreen" allowfullscreen></iframe>
	"""

def bb64_soundcloud(tag_name, value, options, parent, context):
	return f"""
		<iframe 
			width="100%" height="300" 
			scrolling="no" 
			frameborder="no" 
			src="https://w.soundcloud.com/player/?url={value}"></iframe>
	"""

def bb64_flash(tag_name, value, options, parent, context):
	width = '640'
	height = '360'
	if 'width' in options:
		width = options['width']
	if 'height' in options:
		height = options['height']
	return f"""
		<object type="application/x-shockwave-flash" 
			data="{value}" 
			width="{width}" height="{height}">
			<param name="movie" value="{value}" />
			<param name="quality" value="high"/>
		</object>
	"""

def bb64_rand(tag_name, value, options, parent, context):
	choices = re.split(r"\[[oO0*@+x#|]\]", value)
	return choices[random.randint(0, len(choices)-1)]

def bb64_paypal(tag_name, value, options, parent, context):
	paypal_button_id = value.split("/")[-1]
	return f"""
		<form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_top">
			<input type="hidden" name="cmd" value="_s-xclick" />
			<input type="hidden" name="hosted_button_id" value="{paypal_button_id}" />
			<input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_donate_LG.gif" border="0" name="submit" title="PayPal - The safer, easier way to pay online!" alt="Donate with PayPal button" />
		</form>"""

def bb64_markdown(tag_name, value, options, parent, context):
	return markdown(value)

def bbcode64(entry, current_user=None):
	parser = Parser(newline='</p><p>')
	
	parser.add_simple_formatter('ul', '<ul>%(value)s</ul>')
	parser.add_simple_formatter('ol', '<ol>%(value)s</ol>')
	parser.add_simple_formatter('li', '<li>%(value)s</li>')
	parser.add_simple_formatter('h1', '<h1>%(value)s</h1>')
	parser.add_simple_formatter('h2', '<h2>%(value)s</h2>')
	parser.add_simple_formatter('h3', '<h3>%(value)s</h3>')
	parser.add_simple_formatter('h4', '<h4>%(value)s</h4>')
	parser.add_simple_formatter('h5', '<h5>%(value)s</h5>')
	parser.add_simple_formatter('h6', '<h6>%(value)s</h6>')
	parser.add_simple_formatter('tt', '<pre>%(value)s</pre>')
	parser.add_simple_formatter('br', '<br />', standalone=True)
	parser.add_simple_formatter('o', '<span style="text-decoration: overline;">%(value)s</span>')
	parser.add_simple_formatter('u2', '<span style="border-bottom: 1px dotted;">%(value)s</span>')
	parser.add_simple_formatter('em', '<span style="color:#FFF; background-color: #CC0000;">%(value)s</span>')
	parser.add_simple_formatter('ln', '<hr />', standalone=True)

	parser.add_formatter('img', bb64_img, replace_links=False)
	parser.add_simple_formatter('right', '<span class="bbcode-right">%(value)s</span>', transform_newlines=False)
	parser.add_formatter('rev', bb64_rev)
	parser.add_formatter('font', bb64_font)
	parser.add_formatter('size', bb64_size)
	parser.add_formatter('tnail', bb64_tnail, replace_links=False)
	parser.add_formatter('hide', bb64_hide("Hide: "))
	parser.add_formatter('show', bb64_hide("Hide: ", show=True))
	parser.add_formatter('nsfw', bb64_hide("NSFW: ", is_nsfw=True))
	parser.add_formatter('shh', bb64_shh(current_user))
	parser.add_formatter('blind', bb64_blind(current_user))
	parser.add_formatter('profile', bb64_profile, standalone=True)
	parser.add_formatter('h5audio', bb64_h5audio, replace_links=False)
	parser.add_formatter('h5audio', bb64_h5video, replace_links=False)
	parser.add_formatter('audio', bb64_h5audio, replace_links=False)
	parser.add_formatter('youtube', bb64_youtube, replace_links=False)
	parser.add_formatter('youtubehd', bb64_youtube, replace_links=False)
	parser.add_formatter('youtubeaudio', bb64_youtube, replace_links=False)
	parser.add_formatter('vimeo', bb64_vimeo, replace_links=False)
	parser.add_formatter('soundcloud', bb64_soundcloud, replace_links=False)
	parser.add_formatter('flash', bb64_flash, replace_links=False)
	parser.add_formatter('paypal', bb64_paypal, replace_links=False)
	parser.add_simple_formatter('theusertag', current_user.username if current_user else '', standalone=True)
	parser.add_formatter('rand', bb64_rand)
	parser.add_formatter('markdown', bb64_markdown)
	entry = parser.format(entry.entry.strip())
	return format_html('<p>{}</p>',mark_safe(entry))

