from django import forms
from django.urls import reverse
from django.forms import Textarea

from .models import Post, Comment

from crispy_forms.helper import FormHelper

class CrispyForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(CrispyForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)

class PostForm(CrispyForm):
	class Meta:
		model = Post
		fields = ['title','entry','private','show_recent']
		labels = {
			'show_recent': 'Show on Front Page',
			'private': 'Visibility'
		}

class CommentForm(CrispyForm):
	class Meta:
		model = Comment
		fields = ['entry']
		labels = {
			'entry': ''
		}
		widgets = {
			'entry': Textarea(attrs={'cols': 40, 'rows': 4})
		}

