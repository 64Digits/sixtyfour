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
	return render(request, 'user/home.html', {'posts':posts})

def post_listing(request, username, page=1):
	user = get_user_model().objects.get(username=username)
	post_set = Post.objects.filter(user__username=username, deleted=0).order_by('-created')
	paginator = Paginator(post_set, 10)
	posts = paginator.get_page(page)
	return render(request, 'user/listing.html', {'op':user, 'posts':posts})

def post_detail(request, username, entry, page=1):
	user = get_user_model().objects.get(username=username)
	post = Post.objects.get(user__username=username, id=entry)
	comments_set = Comment.objects.filter(post=post, deleted=0)
	paginator = Paginator(comments_set, 10)
	comments = paginator.get_page(page)
	return render(request, 'user/post.html', {'op':user, 'post':post, 'comments':comments})