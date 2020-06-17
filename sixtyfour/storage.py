import os,re,unicodedata
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from sixtyfour.filetypes import get_filetype

class OverwriteStorage(FileSystemStorage):
	def get_available_name(self, name, max_length=None):
		self.delete(name)
		return name

def ensure_directory(path):
		if not default_storage.exists(path):
			sentinel = default_storage.save(os.path.join(path, 'sentinel'), ContentFile(b''))
			default_storage.delete(sentinel)

def is_subdirectory(subdirectory, topdirectory):
		return default_storage.path(subdirectory).startswith(default_storage.path(topdirectory))

def get_fileinfo(f):
		filename = os.path.split(f)[1]
		filetype = get_filetype(filename)
		return {
			'name': filename,
			'type':  filetype,
			'preview': filetype in ('image','audio','video'),
			'size': default_storage.size(f),
			'date': default_storage.get_modified_time(f),
			'url': default_storage.url(f),
		}

# The following are not related to default storage but OS paths generally

def yield_filelist(directory):
	for directory, _, filelist in os.walk(directory):
		for filename in filelist:
			filename = os.path.join(directory, filename)
			if os.path.isfile(filename) or os.path.isdir(filename):
				yield filename

def get_filelist(directory,relative=None):
	if relative:
		return [os.path.relpath(filename,relative) for filename in yield_filelist(directory)]
	else:
		return [filename for filename in yield_filelist(directory)]

def safe_filepath(filepath):
	return re.sub(r'[^\w\s/.-]','',unicodedata.normalize('NFKC',str(filepath))).strip()

def safe_filename(filename):
	return re.sub(r'[^\w\s.-]','',unicodedata.normalize('NFKC',str(filename))).strip()
