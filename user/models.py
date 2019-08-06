from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from sixtyfour.formatters import bbcode64

def get_sentinel_user():
	return get_user_model().objects.get_or_create(username='deleted')[0]

class Profile(models.Model):
	avatar = models.URLField()
	profile = models.TextField()
	location = models.CharField(max_length=40)
	hit_counter = models.IntegerField()
	old_password = models.CharField(max_length=512, default=None)
	
	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete = models.CASCADE,
		primary_key = True
	)

	def __str__(self):
		return 'Profile: %s' % (self.user.username)

class PostManager(models.Manager):
	def get_queryset(self):
		return super().get_queryset().filter(deleted=False)

class FrontPostManager(models.Manager):
	def get_queryset(self):
		return super().get_queryset().filter(deleted=False, pinned=False, show_recent=True)

class NewsPostManager(models.Manager):
	def get_queryset(self):
		return super().get_queryset().filter(deleted=False, pinned=True, show_recent=True)

class UserPostManager(models.Manager):
	def get_queryset(self):
		return super().get_queryset().filter(deleted=False)

class Post(models.Model):
	title = models.CharField(max_length=100)
	entry = models.TextField()

	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)

	show_recent = models.BooleanField(default=True)
	pinned = models.BooleanField(default=False)
	locked = models.BooleanField(default=False)
	deleted = models.BooleanField(default=False)

	user = models.ForeignKey(
		get_user_model(),
		on_delete=models.SET(get_sentinel_user)
	)

	objects = models.Manager()
	posts = PostManager()
	posts_front = FrontPostManager()
	posts_news = NewsPostManager()
	posts_user = UserPostManager()

	@property
	def formatted(self):
		return bbcode64(self)

	def __str__(self):
		return '[%s] %s' % (self.user.username,self.title)
	
	@property
	def comments_count(self):
		return Comment.comments.filter(post=self).count()

	class Meta:
		ordering = ['-created']

class CommentManager(models.Manager):
	def get_queryset(self):
		return super().get_queryset().filter(deleted=False)

class Comment(models.Model):
	entry = models.TextField()

	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(auto_now=True)
	
	deleted = models.BooleanField(default=False)
	
	post = models.ForeignKey(Post, on_delete=models.CASCADE)
	user = models.ForeignKey(
		get_user_model(),
		on_delete=models.SET(get_sentinel_user)
	)

	objects = models.Manager()
	comments = CommentManager()

	@property
	def formatted(self):
		return bbcode64(self)

	class Meta:
		ordering = ['created']
