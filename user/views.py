from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.core.exceptions import PermissionDenied

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

from crispy_forms.layout import Submit

from .models import Post, Comment
from .forms import PostForm

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
		return {
			'post': post,
			'op': post.user,
		}

	def get_queryset(self):
		entry = self.kwargs['entry']
		return Comment.comments.filter(post__id=entry, parent=None)

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
		return super().form_valid(form)
