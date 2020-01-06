from django import forms
from django.urls import reverse
from django.forms import Textarea

from .models import Post, Comment

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Submit

class CrispyModelForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(CrispyModelForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)

class CrispyForm(forms.Form):
	def __init__(self, *args, **kwargs):
		super(CrispyForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper(self)

class PostForm(CrispyModelForm):
	class Meta:
		model = Post
		fields = ['title','entry','private','show_recent']
		labels = {
			'show_recent': 'Show on Front Page',
			'private': 'Visibility'
		}

class CommentForm(CrispyModelForm):
	class Meta:
		model = Comment
		fields = ['entry']
		labels = {
			'entry': ''
		}
		widgets = {
			'entry': Textarea(attrs={'cols': 40, 'rows': 4})
		}

class ConfirmDeleteForm(CrispyForm):
	def __init__(self, *args, **kwargs):
		super(ConfirmDeleteForm, self).__init__(*args, **kwargs)
		self.helper.add_input(Submit('submit', 'Cancel', css_class='btn-secondary'))
		self.helper.add_input(Submit('submit', 'Delete', css_class='btn-primary'))
