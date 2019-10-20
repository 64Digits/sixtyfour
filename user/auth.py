from django.conf import settings
from django.contrib.auth import get_user_model
from hashlib import sha1, md5
import bcrypt
User = get_user_model()

def check_bcrypt(pw,pw_hash):
	return bcrypt.hashpw(pw.encode(),pw_hash.encode()) == pw_hash.encode()

def check_bh1(pw):
	return md5(sha1(md5(pw.encode()).hexdigest().encode()).hexdigest().encode()).hexdigest()

def check_bh2(pw):
	return sha1((settings.LEGACY_SALT_TOKEN+pw).encode()).hexdigest()

def check_badhash(pw,pw_hash):
	return pw_hash==check_bh1(pw) or pw_hash==check_bh2(pw)

def check_legacy(pw,pw_hash):
	return check_bcrypt(pw,pw_hash) or check_badhash(pw,pw_hash)

# Actually mitch redo this and make it the only backend
# Make it authenticate the user and we can control it in the future:
# - prevent banned users logging in
# - rate limiting, etc

class LegacyBackend:
	def authenticate(self, request, username=None, password=None):
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			return None
		pw_hash = user.profile.old_password
		# This backend is only responsible for migrating passwords
		# It always returns None to pass actual authentication through to default ModelBackend
		if user.password == '' and pw_hash and check_legacy(password,pw_hash):
			user.set_password(password)
			user.profile.old_password = ''
			user.profile.save()
			user.save()
		return None

	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None
