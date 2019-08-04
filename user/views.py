from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Post, Comment

from django.contrib.auth import get_user_model

def home_page(request, page=1):
	post_set = Post.objects.filter(deleted=0).order_by('-created')
	paginator = Paginator(post_set, 10)
	posts = paginator.get_page(page)
	return render(request, 'user/home.html', {'posts':posts, 'page':page})

def post_listing(request, username, page=1):
	user = get_user_model().objects.get(username=username)
	post_set = Post.objects.filter(user__username=username).order_by('-created')
	paginator = Paginator(post_set, 10)
	posts = paginator.get_page(page)
	return render(request, 'user/listing.html', {'user':user, 'posts':posts, 'page':page})

def post_detail(request, username, entry):
	user = get_user_model().objects.get(username=username)
	post = Post.objects.get(user__username=username, id=entry)
<<<<<<< HEAD
	return render(request, 'user/post.html', {'user':user, 'post':post})
=======
	comments = Comment.objects.filter(post__id=entry).order_by('created')
	return render(request, 'user/post.html', {'user':user, 'post':post, 'comments':comments})
>>>>>>> Add comments to post detail template

