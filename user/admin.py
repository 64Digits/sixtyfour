from django.contrib import admin

# Register your models here.

from .models import Post,Comment

class CommentInline(admin.TabularInline):
	model = Comment
	extra = 1
	fields = ['entry','user','deleted']

class PostAdmin(admin.ModelAdmin):
	list_display = ('title','user','created')
	inlines = [CommentInline]

admin.site.register(Post, PostAdmin)

