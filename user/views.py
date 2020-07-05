from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView

from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from crispy_forms.layout import Div, Submit

from .models import Post, Comment, Profile
from .forms import PostForm, CommentForm, ConfirmDeleteForm, UserForm, UserProfileForm

from sixtyfour.sidebar import Sidebar,WithSidebar

class WelcomeBar(Sidebar):
	name = "welcome"
	title = "Welcome"

class ProfileBar(Sidebar):
	name = "profile"
	title = "Profile"

class LoginBar(Sidebar):
	name = "login"
	title = "Login"

class LoggedInBar(Sidebar):
	name = "loggedin"
	title = "Actions"

class FrontListView(WithSidebar,ListView):
	template_name = 'user/home.html'	
	context_object_name = 'posts'
	paginate_by = 10
	context = {'heading':'Recent Posts'}
	sidebars = [WelcomeBar()]

	def get_queryset(self):
		return Post.posts_visible(self.request.user).filter(show_recent=True)

class NewsListView(FrontListView):
	context = {'heading':'Recent News'}

	def get_queryset(self):
		return Post.posts_visible(self.request.user).filter(pinned=True, show_recent=True)

class UserPostListView(WithSidebar,ListView):
	template_name = 'user/listing.html'
	context_object_name = 'posts'
	sidebars = [ProfileBar()]
	paginate_by = 10

	def with_context(self,context):
		return {
			'op': get_object_or_404(get_user_model(),username=self.kwargs['username']),
		}

	def get_queryset(self):
		user = self.kwargs['username']
		return Post.posts_visible(self.request.user).filter(user__username=user)

class PostCommentListView(WithSidebar,ListView):
	template_name = 'user/post.html'
	context_object_name = 'comments'
	sidebars = [ProfileBar()]
	paginate_by = 10

	def with_context(self,context):
		post = get_object_or_404(Post.posts,id=self.kwargs['entry'])
		if not post.user_can_view(self.request.user):
			raise PermissionDenied
		form = CommentForm()
		form.helper.form_action = self.request.get_full_path()
		sub = Submit('submit', 'Post Comment')
		sub.field_classes = 'btn btn-sm btn-outline-secondary'
		form.helper.add_layout(Div(
			form.helper.layout,
			Div(sub, css_class='d-flex flex-row-reverse mb-3')
		))
		return {
			'post': post,
			'form': form,
			'op': post.user,
		}

	def get_queryset(self):
		entry = self.kwargs['entry']
		return Comment.comments.filter(post__id=entry, parent=None)

	def post(self, request, *args, **kwargs):
		post = get_object_or_404(Post.posts,id=self.kwargs['entry'])
		form = CommentForm(request.POST)
		if form.is_valid() and request.user.is_authenticated:
			if post.locked or post.deleted:
				raise PermissionDenied
			entry = request.POST['entry']
			obj = Comment.objects.create(user=request.user, post=post, entry=entry)

		return HttpResponseRedirect(request.get_full_path())

class PostCreate(LoginRequiredMixin,WithSidebar,CreateView):
	model = Post
	form_class = PostForm

	def get_form(self, form_class=None):
		form = super().get_form(form_class)
		form.helper.form_action = reverse('sixtyfour:submit')
		form.helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
		return form

	def form_valid(self, form):
		form.instance.user = self.request.user
		return super().form_valid(form)

class PostUpdate(LoginRequiredMixin,WithSidebar,UpdateView):
	model = Post
	form_class = PostForm

	def permission_check(self, form):
		can_edit = form.instance.user == self.request.user 
		if not self.request.user.is_staff:
			can_edit = can_edit and not form.instance.locked
		if not can_edit:
			raise PermissionDenied

	def get_form(self, form_class=None):
		form = super().get_form(form_class)
		self.permission_check(form)
		form.helper.form_action = reverse('user:post_edit', kwargs={'username': self.object.user.username, 'pk': self.object.id} )
		form.helper.add_input(Submit('submit', 'Save', css_class='btn-primary'))
		return form

	def form_valid(self, form):
		self.permission_check(form)
		form.instance.updated = timezone.now()
		return super().form_valid(form)

class CommentUpdate(LoginRequiredMixin,WithSidebar,UpdateView):
	model = Comment
	form_class = CommentForm

	def permission_check(self, form):
		can_edit = form.instance.user == self.request.user
		if not self.request.user.is_staff:
			can_edit = can_edit and not form.instance.post.locked
		if not can_edit:
			raise PermissionDenied

	def get_form(self, form_class=None):
		form = super().get_form(form_class)
		self.permission_check(form)
		form.helper.form_action = reverse('user:comment_edit', kwargs={'pk': self.object.id})
		form.helper.add_input(Submit('submit', 'Save', css_class='btn-primary'))
		return form

	def form_valid(self, form):
		self.permission_check(form)
		form.instance.updated = timezone.now()
		return super().form_valid(form)

	def get_success_url(self):
		return reverse('user:post', kwargs={
			'username': self.object.post.user.username, 
			'entry': self.object.post.id
		})

class PostDelete(LoginRequiredMixin,WithSidebar,TemplateView):
	template_name = 'user/post_delete.html'
	sidebars = [ProfileBar()]

	def with_context(self,context):
		post = get_object_or_404(Post.posts,id=self.kwargs['pk'])
		if not post.user_can_view(self.request.user) or post.user != self.request.user:
			raise PermissionDenied
		self.form = ConfirmDeleteForm()
		self.form.helper.form_action = self.request.get_full_path()
		return {
			'post': post,
			'form': self.form,
			'op': post.user,
		}

	def post(self, request, *args, **kwargs):
		form = ConfirmDeleteForm(request.POST)

		if form.is_valid():
			action = request.POST.get('submit', 'Cancel')
			if action == 'Delete':
				post = get_object_or_404(Post.posts,id=self.kwargs['pk'])
				if post.user != request.user:
					raise PermissionDenied
				post.deleted = True
				post.updated = timezone.now()
				post.save()
				redirect = reverse('user:listing', kwargs={'username':request.user.username})
				return HttpResponseRedirect(redirect)

		redirect = reverse('user:post', kwargs={'username':request.user.username, 'entry':self.kwargs['pk']})
		return HttpResponseRedirect(redirect)

class CommentDelete(LoginRequiredMixin,WithSidebar,TemplateView):
	template_name = 'user/comment_delete.html'
	sidebars = [ProfileBar()]

	def with_context(self,context):
		comment = get_object_or_404(Comment.comments,id=self.kwargs['pk'])
		if not comment.post.user_can_view(self.request.user) or comment.user != self.request.user:
			raise PermissionDenied
		self.form = ConfirmDeleteForm()
		self.form.helper.form_action = self.request.get_full_path()
		return {
			'comment': comment,
			'form': self.form,
			'op': comment.post.user,
		}

	def post(self, request, *args, **kwargs):
		form = ConfirmDeleteForm(request.POST)

		if form.is_valid():
			action = request.POST.get('submit', 'Cancel')
			if action == 'Delete':
				comment = get_object_or_404(Comment.comments,id=self.kwargs['pk'])
				if comment.user != request.user:
					raise PermissionDenied
				comment.deleted = True
				comment.updated = timezone.now()
				comment.save()
				redirect = reverse('user:post', kwargs={'username':request.user.username, 'entry':comment.post.id})
				return HttpResponseRedirect(redirect)

		comment = get_object_or_404(Comment.comments,id=self.kwargs['pk'])
		redirect = reverse('user:post', kwargs={'username':request.user.username, 'entry':comment.post.id})
		return HttpResponseRedirect(redirect)

class PreferencesView(LoginRequiredMixin,WithSidebar,TemplateView):
	template_name = 'user/preferences.html'
	sidebars = [ProfileBar()]

	def with_context(self,context):
		user = self.request.user
		uf = UserForm(prefix="uf",instance=user)
		upf = UserProfileForm(prefix="upf",instance=user.profile)
		return {
			'op': user,
			'user_form':uf,
			'profile_form':upf
		}

	def post(self, request, *args, **kwargs):
		user = request.user
		uf = UserForm(request.POST,prefix="uf",instance=user)
		upf = UserProfileForm(request.POST,request.FILES,prefix="upf",instance=user.profile)
		if upf.is_valid() and uf.is_valid():
			upf.save()
			uf.save()
			redirect = reverse('user:listing', kwargs={'username':request.user.username})
			return HttpResponseRedirect(redirect)
