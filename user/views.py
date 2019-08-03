from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from .models import Post, Comment

from django.contrib.auth import get_user_model

# testing a couple views

def post_listing(request, username, page=1):
	# TODO: use django pagination class
	user = get_user_model().objects.get(username=username)
	posts = Post.objects.filter(user__username=username).order_by('-created')[:10]
	#return HttpResponse(str(posts),content_type="text/plain")
	return render(request, 'user/listing.html', {'user':user,'posts':posts})

def post_detail(request, username, entry):
	# TODO: create templates
	post = Post.objects.filter(user__username=username, id=entry)
	return HttpResponse(str(post),content_type="text/plain")

