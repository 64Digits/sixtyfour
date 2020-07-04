from django.contrib import admin

from .models import AuthLog

class AuthLogAdmin(admin.ModelAdmin):
	model = AuthLog
	readonly_fields = ['date','user','ip_address','city','region','country','continent']
	list_display = ['date','user','ip_address','city','region','country','continent']
	list_display_links = None
	list_filter = ['date']
	list_select_related = ['user']
	ordering = ['-date']
	search_fields = ['=user__username','=ip_address','=city','=region','=country','=continent']

	def has_add_permission(self, request, obj=None):
		return False

	def has_delete_permission(self, request, obj=None):
		return False

	def save_model(self, request, obj, form, change):
		pass

	def delete_model(self, request, obj):
		pass

	def save_related(self, request, form, formsets, change):
		pass

admin.site.register(AuthLog,AuthLogAdmin)
