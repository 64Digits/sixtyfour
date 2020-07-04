from django.db import models
from django.contrib.auth import get_user_model
from user.models import get_sentinel_user

class AuthLog(models.Model):
	ip_address = models.GenericIPAddressField()
	city = models.CharField(max_length=32,blank=True)
	region = models.CharField(max_length=2,blank=True)
	country = models.CharField(max_length=2,blank=True)
	continent = models.CharField(max_length=2,blank=True)

	date = models.DateTimeField(auto_now_add=True)

	user = models.ForeignKey(
		get_user_model(),
		on_delete=models.SET(get_sentinel_user)
	)

	def __str__(self):
		return '%s login from %s' % (self.user.username,self.ip_address)
