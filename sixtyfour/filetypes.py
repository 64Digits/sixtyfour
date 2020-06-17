import os,mimetypes
from sixtyfour.settings import STATIC_URL

file_extensions = {
	'image': ['.bmp','.gif','.png','.apng','.jpx','.jpg','.jpeg','.webp','.ico','.svg'],
	'archive': ['.zip','.7z','.rar','.tar','.gz','.tgz','.xz','.txz','.bz',
		'.tbz','.bz2'],
	'text': ['.txt','.json','.csv','.js','.css','.py','.php','.c','.h','.cpp','.cc',
		'.hpp','.java','.xml','.lsp','.nim','.sql','.lua','.ps1','.go','.rs','.rb','.yml',
		'.json5','.ini','.toml','.hs','.cs','.r','.lsp','.glsl','.cg','.sh','.bat','.cmd'],
	'document': ['.pdf','.md','.html','.htm','.doc','.xls','.ppt','.docx',
		'.xlsx','.pptx','.odt','.ods','.odp','.ps','.rtf'],
	'executable': ['.exe','.jar','.bin','.swf','.run','.out','.mpkg','.apk','.msi',
		'.deb','.rpm','.appimage'],
	'video': ['.mp4','.webm','.mkv','.mpeg','.mov','.avi','.wmv','.flv','.ogv',
		'.ts','.3gp','.3g2'],
	'audio': ['.mp3','.ogg','.flac','.wav','.aac','.weba','.opus','.midi'],
}

mime_filetypes = {}
for filetype,extensions in file_extensions.items():
	for ext in extensions:
		mime_filetypes[ext] = filetype

def get_filetype(url):
	_, ext = os.path.splitext(url)
	ext = ext.lower()
	if ext in mime_filetypes:
		return mime_filetypes[ext]
	try:
		mime = mimetypes.guess_type(url)[0]
		mime_general = mime.split('/')[0]
		if mime_general in ['text','audio','video','image']:
			return mime_general
	except Exception:
		pass
	return 'file'

def get_filetype_ext(url):
	ext, mime, mime_general = '','',''
	try:
		_, ext = os.path.splitext(url)
		mime = mimetypes.guess_type(url)[0]
		mime_general = mime.split('/')[0]
	except Exception:
		pass
	return ext,mime,mime_general

def get_fileicon(url):
	return '{}/images/icons/file_{}.png'.format(STATIC_URL,get_filetype(url))

def is_image(url):
	_, ext = os.path.splitext(url)
	return ext in file_extensions['image']

