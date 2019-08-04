from bbcode import Parser

def bbcode64(entry):
	parser = Parser(newline='</p><p>')
	
	return '<p>'+parser.format(entry.entry)+'</p>'

