from django import forms
from django.urls import reverse
from django.forms import Textarea,CheckboxSelectMultiple

from .models import Post, Comment, Profile
from django.contrib.auth import get_user_model

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout, Submit
from crispy_forms.bootstrap import InlineField

from django.contrib.auth.forms import PasswordChangeForm
from django_registration.forms import RegistrationFormCaseInsensitive, RegistrationFormTermsOfService

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

class UserForm(CrispyModelForm):
	def __init__(self, *args, **kwargs):
		super(UserForm, self).__init__(*args, **kwargs)
		self.helper.form_tag = False

	class Meta:
		model = get_user_model()
		fields = ['last_name','email']
		labels = {
			'last_name': 'Name',
			'email': 'Email Address'
		}

class UserProfileForm(CrispyModelForm):
	def __init__(self, *args, **kwargs):
		super(UserProfileForm, self).__init__(*args, **kwargs)
		self.helper.form_tag = False
		self.helper.add_input(Submit('submit', 'Save', css_class='btn-primary'))

	class Meta:
		model = Profile
		fields = ['profile','avatar','banner']

class PasswordChangeForm(PasswordChangeForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper(self)
		self.helper.add_input(Submit('submit', 'Change Password', css_class='btn-primary'))

class UploadFilesForm(CrispyForm):
	files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

	def __init__(self, *args, **kwargs):
		super(UploadFilesForm, self).__init__(*args, **kwargs)
		self.helper.form_tag = False
		self.helper.form_show_labels = False

class CreateFolderForm(CrispyForm):
	new_folder = forms.CharField(strip=True)

	def __init__(self, *args, **kwargs):
		super(CreateFolderForm, self).__init__(*args, **kwargs)
		self.helper.form_tag = False
		self.helper.form_show_labels = False

class FileRenameForm(forms.Form):
	old_name = forms.CharField(strip=True)
	new_name = forms.CharField(strip=True)

class FileDeleteForm(forms.Form):
	delete = forms.CharField(strip=True)

class RegistrationForm(RegistrationFormCaseInsensitive, RegistrationFormTermsOfService):
	pass

bulk_actions = [
	('visible_only_me','Set Visible to Only Me'),
	('visible_registered','Set Visible to Registered Users'),
	('visible_regular','Set Visible to Regular Users'),
	('visible_public','Set Visible to Public'),
	('visible_staff','Set Visible to Staff'),
	('delete','Delete Posts (NO UNDO)'),
]

class UserManagePostsForm(CrispyForm):
	posts = forms.ModelMultipleChoiceField(queryset=None,widget=CheckboxSelectMultiple)
	action = forms.ChoiceField(choices=bulk_actions)
	def __init__(self, user, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['posts'].queryset = Post.posts_visible(user).filter(user=user)
		self.helper.form_tag = False
		self.helper.field_template = 'bootstrap4/layout/inline_field.html'
		self.helper.layout = Div(Layout(
				InlineField('action', css_class='flex-grow-1'),
				Submit('submit', 'Update Posts', css_class='btn-primary ml-3'),
		),css_class='form-inline justify-content-end')

from django.utils import timezone
class UserManagePostsByDateForm(CrispyForm):
	older_than = forms.DateTimeField(initial=timezone.now)
	action = forms.ChoiceField(choices=bulk_actions)
	confirm = forms.BooleanField(initial=False, required=True)
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper.add_input(Submit('submit', 'Update Posts', css_class='btn-primary'))
