import os, re, shutil
from django.views.generic import TemplateView

from django.shortcuts import render
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, Http404
from django.core.files.storage import default_storage

from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import UploadFilesForm, CreateFolderForm, FileRenameForm, FileDeleteForm

from sixtyfour.sidebar import Sidebar,WithSidebar
from sixtyfour.filetypes import get_filetype, get_filetype_ext
from sixtyfour.storage import ensure_directory, is_subdirectory, get_fileinfo, get_filelist, safe_filename, safe_filepath

class FileManagerBar(Sidebar):
	name = "filemanager"
	title = "File Manager"

class FileManagerView(LoginRequiredMixin,WithSidebar,TemplateView):
	template_name = 'user/filemanager.html'
	sidebars = [FileManagerBar()]

	def get_basedir(self):
		return os.path.join('users',self.request.user.username)

	def allowed_filetype(self,filename):
		uploadtype = get_filetype(filename, True)
		ext, _, _ = get_filetype_ext(filename)
		return (uploadtype != 'file' or ext == '') and not ext.lower() in ['.js', '.htm', '.html']

	def with_context(self,context):
		user = self.request.user
		base_dir = self.get_basedir()
		ensure_directory(base_dir)
		nav_dir = self.request.GET.get('folder','')
		working_dir = os.path.join(base_dir, nav_dir)

		if not default_storage.exists(working_dir):
			raise Http404
		if not is_subdirectory(working_dir, base_dir):
			raise PermissionDenied

		breadcrumbs, cons, skip = [], "", True
		dir_walk = os.path.normpath(os.path.join(user.username,nav_dir)).split(os.path.sep)
		for d in dir_walk:
			if not skip:
				cons = os.path.join(cons, d)
			skip = False
			breadcrumbs += [{'name': d,'nav_dir': cons}]
		breadcrumbs[-1]['current'] = True

		dirnames,filenames = default_storage.listdir(working_dir)
		dirs = list(map(lambda d: {'name': d,'nav_dir': os.path.join(nav_dir,d)}, dirnames))
		dirs.sort(key=lambda d: d['name'])

		files = list(map(lambda f: get_fileinfo(os.path.join(working_dir,f)),filenames))
		files.sort(key=lambda f: f['type']+f['name'])

		upload_form = UploadFilesForm()
		folder_form = CreateFolderForm()
		return {
			'nav_dir': nav_dir,
			'dirs': dirs,
			'files': files,
			'op': user,
			'breadcrumbs': breadcrumbs,
			'upload_form': upload_form,
			'folder_form': folder_form,
		}

	def post(self, request, *args, **kwargs):
		user = request.user
		base_dir = self.get_basedir()
		ensure_directory(base_dir)
		nav_dir = self.request.POST.get('folder','')
		working_dir = os.path.join(base_dir, nav_dir)

		if not default_storage.exists(working_dir):
			raise Http404
		if not is_subdirectory(working_dir, base_dir):
			raise PermissionDenied

		upload_form = UploadFilesForm(request.POST,request.FILES)
		folder_form = CreateFolderForm(request.POST)
		file_rename_form = FileRenameForm(request.POST)
		file_delete_form = FileDeleteForm(request.POST)

		if upload_form.is_valid():
			files = request.FILES.getlist('files')
			for f in files:
				if self.allowed_filetype(f.name):
					uploadname = safe_filename(f.name)
					new_file = os.path.join(working_dir, uploadname)
					default_storage.save(new_file, f)

		if folder_form.is_valid():
			new_dirname = safe_filename(folder_form.cleaned_data['new_folder'])
			new_dir = os.path.join(working_dir, new_dirname)
			if is_subdirectory(new_dir, working_dir):
				ensure_directory(new_dir)

		if file_rename_form.is_valid():
			old_name = file_rename_form.cleaned_data['old_name']
			new_name = safe_filepath(file_rename_form.cleaned_data['new_name'])
			old_path = os.path.join(working_dir,old_name)
			new_path = os.path.join(working_dir,new_name)
			if not default_storage.exists(old_path):
				raise Http404
			if not is_subdirectory(old_path, base_dir) or not is_subdirectory(new_path, base_dir):
				raise PermissionDenied
			if self.allowed_filetype(new_name):
				old_path = default_storage.path(old_path)
				new_path = default_storage.path(new_path)
				os.rename(old_path,new_path)

		if file_delete_form.is_valid():
			delete_name = file_delete_form.cleaned_data['delete']
			delete_path = os.path.join(working_dir,delete_name)
			if not default_storage.exists(delete_path):
				raise Http404
			if not is_subdirectory(delete_path, base_dir):
				raise PermissionDenied
			delete_realpath = default_storage.path(delete_path)
			is_dir = os.path.isdir(delete_realpath)
			if request.POST.get("confirm", False):
				if is_dir:
					shutil.rmtree(delete_realpath)
				else:
					os.remove(delete_realpath)
			else:
				if is_dir:
					filelist = get_filelist(delete_realpath,default_storage.path(working_dir))
				else:
					filelist = None
				return render(request, 'user/file_delete.html', {
					'name': delete_name,
					'directory': is_dir,
					'filelist': filelist,
					'nav_dir':nav_dir,
				})

		redirect = reverse('sixtyfour:filemanager')
		if nav_dir:
			redirect += '?folder={}'.format(nav_dir)
		return HttpResponseRedirect(redirect)
