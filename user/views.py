from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from .models import Post, Comment

# testing a couple views

def post_listing(request, username, page=1):
	# TODO: use django pagination class
	# TODO: create templates
	posts = Post.objects.filter(user__username=username).order_by('-created')[:10]
	return HttpResponse(str(posts),content_type="text/plain")
	#return render(request, 'user/index.html', {'posts':posts})

def post_detail(request, username, entry):
	# TODO: create templates
	post = Post.objects.filter(user__username=username, id=entry)
	return HttpResponse(str(post),content_type="text/plain")

