import django.contrib.auth.views as auth_views
from user.forms import PasswordChangeForm

from django.urls import reverse_lazy

class PasswordChangeView(auth_views.PasswordChangeView):
	form_class = PasswordChangeForm
	success_url = reverse_lazy('sixtyfour:password_change_done')
