from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from hashlib import sha1, md5
from ipware import get_client_ip
from moderation.models import AuthLog
import bcrypt

try:
	from django.contrib.gis.geoip2 import GeoIP2
except ImportError:
	HAS_GEOIP2 = False
else:
	HAS_GEOIP2 = True
	g = GeoIP2()

User = get_user_model()

def check_bcrypt(pw,pw_hash):
	try:
		return bcrypt.hashpw(pw.encode(),pw_hash.encode()) == pw_hash.encode()
	except ValueError:
		return False

def check_bh1(pw):
	return md5(sha1(md5(pw.encode()).hexdigest().encode()).hexdigest().encode()).hexdigest()

def check_bh2(pw):
	return sha1((settings.LEGACY_SALT_TOKEN+pw).encode()).hexdigest()

def check_badhash(pw,pw_hash):
	return pw_hash==check_bh1(pw) or pw_hash==check_bh2(pw)

def check_legacy(pw,pw_hash):
	return check_bcrypt(pw,pw_hash) or check_badhash(pw,pw_hash)

class DefaultBackend(ModelBackend):
	def authenticate(self, request, username=None, password=None):
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			return None
		pw_hash = user.profile.old_password
		# Migrate old password hash if appropriate
		if user.password == '' and pw_hash and check_legacy(password,pw_hash):
			user.set_password(password)
			user.profile.old_password = ''
			user.profile.save()
			user.save()
		# Defer authentication to ModelBackend
		loginuser = super().authenticate(request, username, password)
		# Log successful login to moderation log
		if loginuser:
			client_ip, is_routable = get_client_ip(request)
			if HAS_GEOIP2 and is_routable:
				try:
					# Store GeoIP data if available
					loc = g.city(client_ip)
					entry = AuthLog(user=loginuser, ip_address=client_ip, city=loc['city'], region=loc['region'], country=loc['country_code'], continent=loc['continent_code'])
					entry.save()
					return loginuser
				except:
					pass
			entry = AuthLog(user=loginuser, ip_address=client_ip)
			entry.save()
		return loginuser
