from django import forms
from django.urls import reverse

from .models import Post

from crispy_forms.helper import FormHelper

class CrispyForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(CrispyForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)

class PostForm(CrispyForm):
	class Meta:
		model = Post
		fields = ['title','entry','private']
		labels = {'private': 'Visibility'}

