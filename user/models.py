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

class PostVisibility():
	PUBLIC=0
	REGISTERED=1
	REGULAR=2
	GROUP=3
	PERSONAL=4
	choices = [
		(PUBLIC, 'Public'),
		(REGISTERED, 'Registered Members'),
		(REGULAR, 'Regular Members'),
		(GROUP, 'Group Members'),
		(PERSONAL, 'Only Me')
	]

class PostManager(models.Manager):
	def get_queryset(self):
		return super().get_queryset().filter(deleted=False)

class FrontPostManager(models.Manager):
	def get_queryset(self):
		return super().get_queryset().filter(deleted=False, show_recent=True, private=PostVisibility.PUBLIC)

class NewsPostManager(models.Manager):
	def get_queryset(self):
		return super().get_queryset().filter(deleted=False, pinned=True, show_recent=True, private=PostVisibility.PUBLIC)

class UserPostManager(models.Manager):
	def get_queryset(self):
		return super().get_queryset().filter(deleted=False, private=PostVisibility.PUBLIC)

class Post(models.Model):
	title = models.CharField(max_length=100)
	entry = models.TextField()

	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(null=True, default=None)

	show_recent = models.BooleanField(default=True)
	pinned = models.BooleanField(default=False)
	locked = models.BooleanField(default=False)
	private = models.SmallIntegerField(
		choices=PostVisibility.choices,
		default=PostVisibility.PUBLIC
	)
	deleted = models.BooleanField(default=False)

	user = models.ForeignKey(
		get_user_model(),
		on_delete=models.SET(get_sentinel_user)
	)

	posts = PostManager()
	posts_front = FrontPostManager()
	posts_news = NewsPostManager()
	posts_user = UserPostManager()
	objects = models.Manager()

	@property
	def comments_count(self):
		return Comment.comments.filter(post=self).count()

	def __str__(self):
		return '[%s] %s' % (self.user.username,self.title)

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

	parent = models.ForeignKey('self', on_delete=models.DO_NOTHING, blank=True, null=True, default=None)

	comments = CommentManager()
	objects = models.Manager()

	@property
	def children(self):
		return self.comment_set.all()

	class Meta:
		ordering = ['created']
