from asyncore import write
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.urls import reverse
from django.dispatch import receiver
from sixtyfour.formatters import bbcode64
import datetime, hashlib, os


def get_sentinel_user():
	return get_user_model().objects.get_or_create(username='deleted')[0]

def user_avatar_path(instance, filename):
	name, ext = os.path.splitext(filename)
	username = instance.user.username
	newname = hashlib.sha1(username.encode('utf-8')).hexdigest() + ext
	return 'profile/avatar/{}'.format(newname)

def user_banner_path(instance, filename):
	name, ext = os.path.splitext(filename)
	username = instance.user.username
	newname = hashlib.sha1(username.encode('utf-8')).hexdigest() + ext
	return 'profile/banner/{}'.format(newname)

class Profile(models.Model):
	avatar = models.ImageField(max_length=128,blank=True,upload_to=user_avatar_path)
	banner = models.ImageField(max_length=128,blank=True,upload_to=user_banner_path)
	profile = models.TextField(blank=True)
	location = models.CharField(max_length=40, blank=True)
	hit_counter = models.IntegerField()
	old_password = models.CharField(max_length=512, blank=True, default='')

	user = models.OneToOneField(
		get_user_model(),
		on_delete = models.CASCADE,
		primary_key = True
	)

	@property
	def url(self):
		return reverse('user:listing', kwargs={'username':self.user.username})

	@property
	def avatar_url(self):
		#return "%s%s" % (settings.AVATAR_URL, self.avatar)
		return self.avatar.url

	@property
	def banner_url(self):
		#return "%s%s" % (settings.BANNER_URL, self.banner)
		return self.banner.url

	@property
	def is_regular(self):
		#return (datetime.now() - self.user.date_joined).days > 90
		# All users are regular users
		return True

	@property
	def entry(self):
		return self.profile

	@receiver(post_save, sender=User)
	def create_user_profile(sender, instance, created, **kwargs):
		if kwargs.get('created', True) and not kwargs.get('raw', False):
			Profile.objects.get_or_create(user=instance,defaults={'hit_counter':0})

	def __str__(self):
		return 'Profile: %s' % (self.user.username)

class PostVisibility():
	PUBLIC=0
	REGISTERED=1
	REGULAR=2
	STAFF=3
	PERSONAL=4
	choices = [
		(PUBLIC, 'Public'),
		(REGISTERED, 'Registered Members'),
		(REGULAR, 'Regular Members'),
		(STAFF, 'Staff Members'),
		(PERSONAL, 'Only Me')
	]

class PostManager(models.Manager):
	def get_queryset(self):
		return super().get_queryset().filter(deleted=False)

class Post(models.Model):
	title = models.CharField(max_length=100)
	entry = models.TextField()

	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(null=True, blank=True, default=None)
	interacted = models.DateTimeField(auto_now_add=True, null=True, blank=True)

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
	objects = models.Manager()

	@property
	def comments_count(self):
		return Comment.comments.filter(post=self).count()

	@property
	def plusone_count(self):
		return PlusOne.plus_ones.filter(targetPost=self).count()

	@property
	def plusone_users(self):
		results = PlusOne.plus_ones.filter(targetPost=self)[:2]
		count = self.plusone_count
		
		def get_names(p):
			return p.user.username

		names = ", ".join(map(get_names, results))

		title = f'This post was +1\'d by {names}'
		if results.count() < count:
			title += f' and {count-2} more...'

		return title

	def add_plusone(self, user):
		existing = PlusOne.plus_ones.filter(user=user,targetPost=self).count() > 0
		if not existing and user.is_authenticated:
			plus = PlusOne(targetType=PlusOne.TargetType.POST, targetPost=self, user=user)
			plus.save()

	def get_absolute_url(self):
		return reverse('user:post', kwargs={'username': self.user.username, 'entry': self.id})

	@property
	def url(self):
		return self.get_absolute_url()

	@staticmethod
	def get_post_query(user):
		query = None
		if user.is_authenticated:
			if user.is_staff:
				query = Q(private__lte=PostVisibility.STAFF)
			elif user.profile.is_regular:
				query = Q(private__lte=PostVisibility.REGULAR)
			else:
				query = Q(private__lte=PostVisibility.REGISTERED)
			query = query | Q(user=user)
		else:
			query = Q(private=PostVisibility.PUBLIC)
		return query
		
	@staticmethod
	def posts_visible(user):
		query = Post.get_post_query(user)
		return Post.posts.filter(query)

	@staticmethod
	def posts_recent(user):
		query = Post.get_post_query(user)
		return Post.posts.filter(query).order_by('interacted').reverse()

	def user_can_view(self, user):
		visible = (self.private == PostVisibility.PUBLIC)
		visible = visible or (self.user == user)
		visible = visible or (user.is_staff)
		if user.is_authenticated:
			visible = visible or (self.private == PostVisibility.REGISTERED)
			visible = visible or (self.private == PostVisibility.REGULAR and user.profile.is_regular)
		return visible

	@property
	def visible_description(self):
		if self.private == PostVisibility.PUBLIC:
			return ''
		else:
			desc = [v[1] for i,v in enumerate(PostVisibility.choices) if v[0] == self.private]
			return 'Visible to %s' % (desc[0])

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
	updated = models.DateTimeField(null=True, blank=True, default=None)

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
	def plusone_count(self):
		return PlusOne.plus_ones.filter(targetComment=self).count()

	@property
	def plusone_users(self):
		results = PlusOne.plus_ones.filter(targetComment=self)[:2]
		count = self.plusone_count
		
		def get_names(p):
			return p.user.username

		names = ", ".join(map(get_names, results))

		title = f'This comment was +1\'d by {names}'
		if results.count() < count:
			title += f' and {count-2} more...'

		return title

	def add_plusone(self, user):
		existing = PlusOne.plus_ones.filter(user=user,targetComment=self).count() > 0
		if not existing and user.is_authenticated:
			plus = PlusOne(targetType=PlusOne.TargetType.COMMENT, targetComment=self, user=user)
			plus.save()

	@property
	def children(self):
		return self.comment_set.all()

	class Meta:
		ordering = ['created']

class PlusOneManager(models.Manager):
	def get_queryset(self):
		return super().get_queryset()

class PlusOne(models.Model):
	class TargetType(models.IntegerChoices):
		COMMENT = 1
		POST = 2

	targetType = models.IntegerField(choices=TargetType.choices)
	targetPost = models.ForeignKey(Post, on_delete=models.DO_NOTHING, blank=True, null=True, default=None)
	targetComment = models.ForeignKey(Comment, on_delete=models.DO_NOTHING, blank=True, null=True, default=None)
	user = models.ForeignKey(get_user_model(), on_delete=models.SET(get_sentinel_user))

	plus_ones = PlusOneManager()
	objects = models.Manager()