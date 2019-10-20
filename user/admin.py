from django.contrib import admin

# Register your models here.

from .models import Post,Comment,Profile

class CommentInline(admin.TabularInline):
	model = Comment
	fields = ['entry','user','parent','deleted']
	raw_id_fields = ('user','parent',)
	readonly_fields = ('id',)
	extra = 1

	def get_queryset(self,request):
		if not hasattr(self, '_queryset'):
			self._queryset = Comment.objects.all()
		return self._queryset

class PostAdmin(admin.ModelAdmin):
	list_display = ('title','user','created')
	raw_id_fields = ('user',)
	inlines = [CommentInline]

admin.site.register(Post, PostAdmin)
admin.site.register(Profile)

