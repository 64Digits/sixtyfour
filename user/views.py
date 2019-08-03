from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Post, Comment

from django.contrib.auth import get_user_model

# testing a couple views

def post_listing(request, username, page=1):
	# TODO: use django pagination class
	user = get_user_model().objects.get(username=username)

	# QuerySets are already optimized for pagination (E.G: They lazy load as needed,
	# so even loading 'all' of the objects doesn't actually load all of them)
	# This might still be a future performance limiter.

	post_set = Post.objects.filter(user__username=username).order_by('-created')
	paginator = Paginator(post_set, 10)
	posts = paginator.get_page(page)

	return render(request, 'user/listing.html', {'user':user,'posts':posts, 'page':page})

def post_detail(request, username, entry):
	post = Post.objects.get(user__username=username, id=entry)
	print(post)
	return render(request, 'user/post.html', {'post':post})

