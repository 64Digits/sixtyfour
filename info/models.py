from django.db import models

class Page(models.Model):
	title = models.CharField(max_length=100)
	key = models.SlugField(max_length=32, unique=True)
	content = models.TextField()

	created = models.DateTimeField(auto_now_add=True)
	updated = models.DateTimeField(null=True, auto_now=True)

	published = models.BooleanField(default=True)

	def __str__(self):
		return '[%s] %s' % (self.key,self.title)

class LinkList(models.Model):
	title = models.CharField(max_length=100)
	key = models.SlugField(max_length=32, unique=True)

	def __str__(self):
		return '[%s] %s' % (self.key,self.title)

class Link(models.Model):
	title = models.CharField(max_length=100)
	url = models.CharField(max_length=256)
	sort = models.PositiveSmallIntegerField(default=0)
	linklist = models.ForeignKey(LinkList, on_delete=models.CASCADE)

	published = models.BooleanField(default=True)
	
	def __str__(self):
		return '[%s](%s)' % (self.title,self.url)
