#from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.shortcuts import render

from .models import Page

class InfoPageView(DetailView):
	template_name = 'info/page.html'
	model = Page
	slug_field = 'key'
