from bbcode import Parser
from django.utils.html import format_html
from django.utils.safestring import mark_safe

def bbcode64(entry):
	parser = Parser(newline='</p><p>')
	entry = parser.format(entry.entry)
	return format_html('<p>{}</p>',mark_safe(entry))

