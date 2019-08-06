from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404

from .models import Post, Comment
from django.contrib.auth import get_user_model

class ListContextView(ListView):
	def add_context(self,context):
		pass
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		self.add_context(context)
		return context

class FrontListView(ListContextView):
	paginate_by = 10
	context_object_name = 'posts'
	template_name = 'user/home.html'	
	queryset = Post.posts_front.order_by('-created')

class UserPostListView(ListContextView):
	paginate_by = 10
	context_object_name = 'posts'
	template_name = 'user/listing.html'
	
	def add_context(self,context):
		context['op'] = get_object_or_404(get_user_model(),username=self.kwargs['username'])
	
	def get_queryset(self):
		user = self.kwargs['username']
		return Post.posts.filter(user__username=user).order_by('-created')

class PostCommentListView(ListContextView):
	paginate_by = 10
	context_object_name = 'comments'
	template_name = 'user/post.html'
	
	def add_context(self,context):
		context['op'] = get_object_or_404(get_user_model(),username=self.kwargs['username'])
		context['post'] = get_object_or_404(Post,id=self.kwargs['entry'])
	
	def get_queryset(self):
		entry = self.kwargs['entry']
		return Comment.objects.filter(post__id=entry).order_by('-created')
