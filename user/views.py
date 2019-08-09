from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404

from .models import Post, Comment
from django.contrib.auth import get_user_model

from sixtyfour.sidebar import Sidebar,WithSidebar

class WelcomeBar(Sidebar):
	name = "welcome"
	title = "Welcome"

class ProfileBar(Sidebar):
	name = "profile"
	title = "Profile"

class FrontListView(WithSidebar,ListView):
	template_name = 'user/home.html'	
	context_object_name = 'posts'
	paginate_by = 10
	queryset = Post.posts_front.all()
	context = {'heading':'Recent Posts'}
	sidebars = [WelcomeBar()]

class NewsListView(FrontListView):
	queryset = Post.posts_news.all()
	context = {'heading':'Recent News'}

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
		return Post.posts_user.filter(user__username=user)

class PostCommentListView(WithSidebar,ListView):
	template_name = 'user/post.html'
	context_object_name = 'comments'
	sidebars = [ProfileBar()]
	paginate_by = 10

	def with_context(self,context):
		post = get_object_or_404(Post,id=self.kwargs['entry'])
		return {
			'post': post,
			'op': post.user,
		}

	def get_queryset(self):
		entry = self.kwargs['entry']
		return Comment.comments.filter(post__id=entry)
