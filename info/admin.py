from django.contrib import admin

# Register your models here.

from .models import Page,LinkList,Link

class LinkInline(admin.TabularInline):
	model = Link
	fields = ['title','url','sort','published']
	extra = 1

	def get_queryset(self,request):
		if not hasattr(self, '_queryset'):
			self._queryset = Link.objects.all().order_by('sort')
		return self._queryset

class LinkListAdmin(admin.ModelAdmin):
	list_display = ('title','key')
	inlines = [LinkInline]

	def get_queryset(self,request):
		if not hasattr(self, '_queryset'):
			self._queryset = LinkList.objects.all()
		return self._queryset

admin.site.register(LinkList,LinkListAdmin)
admin.site.register(Page)
