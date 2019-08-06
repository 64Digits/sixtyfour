from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404

from .models import Post, Comment
from django.contrib.auth import get_user_model

class WithContext():
	def with_context(self,context):
		return {}
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context.update(self.with_context(context))
		return context

class FrontListView(ListView):
	template_name = 'user/home.html'	
	context_object_name = 'posts'
	paginate_by = 10
	queryset = Post.posts_front.all()

class UserPostListView(WithContext,ListView):
	template_name = 'user/listing.html'
	context_object_name = 'posts'
	paginate_by = 10

	def with_context(self,context):
		return {
			'op': get_object_or_404(get_user_model(),username=self.kwargs['username']),
		}

	def get_queryset(self):
		user = self.kwargs['username']
		return Post.posts_user.filter(user__username=user)

class PostCommentListView(WithContext,ListView):
	template_name = 'user/post.html'
	context_object_name = 'comments'
	paginate_by = 10

	def with_context(self,context):
		return {
			'op': get_object_or_404(get_user_model(),username=self.kwargs['username']),
			'post': get_object_or_404(Post,id=self.kwargs['entry']),
		}

	def get_queryset(self):
		entry = self.kwargs['entry']
		return Comment.comments.filter(post__id=entry)
