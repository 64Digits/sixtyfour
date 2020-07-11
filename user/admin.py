from django.contrib import admin
from django.utils.text import slugify

from .models import Post,Comment,Profile,PostVisibility

# Admin Inlines

class CommentInline(admin.TabularInline):
	model = Comment
	fields = ['entry','user','parent','deleted']
	raw_id_fields = ('user','parent',)
	readonly_fields = ('id','updated')
	extra = 1

	def get_queryset(self,request):
		if not hasattr(self, '_queryset'):
			self._queryset = Comment.objects.all()
		return self._queryset

	def has_delete_permission(self, request, obj=None):
		return False

# Actions

def gen_action(field,value,description):
	def action_sub(modeladmin, request, queryset):
		updated = {}
		updated[field] = value
		queryset.update(**updated)
	action_sub.short_description = description
	action_sub.__name__ = 'action_{}'.format(slugify(description))
	return action_sub

post_actions = [
		gen_action('show_recent',True,'Front Post'),
		gen_action('show_recent',False,'Unfront Post'),
		gen_action('locked',True,'Lock Post'),
		gen_action('locked',False,'Unlock Post'),
		gen_action('deleted',True,'Delete Post'),
		gen_action('deleted',False,'Undelete Post'),
		gen_action('pinned',True,'Pin Post'),
		gen_action('pinned',False,'Unpin Post'),
]

for value, name in PostVisibility.choices:
	post_actions.append(
		gen_action('private',value,'Set Visible to {}'.format(name))
	)

comment_actions = [
	gen_action('deleted',True,'Delete Comment'),
	gen_action('deleted',False,'Undelete Comment'),
	gen_action('parent',None,'Unparent Comment'),
]

# ModelAdmins

class PostAdmin(admin.ModelAdmin):
	list_display = ('title','user','created','private','show_recent','pinned','locked','deleted')
	raw_id_fields = ('user',)
	search_fields = ('=user__username','title')
	inlines = [CommentInline]
	actions = post_actions

	def get_queryset(self,request):
		if not hasattr(self, '_queryset'):
			self._queryset = Post.objects.all()
		return self._queryset

	def has_delete_permission(self, request, obj=None):
		return False

class CommentAdmin(admin.ModelAdmin):
	list_display = ['id','user','entry','created','post','parent','deleted']
	fields = ['entry','user','post','parent','deleted']
	raw_id_fields = ('user','post','parent',)
	search_fields = ('=user__username',)
	ordering = ('-created',)
	actions = comment_actions

	def get_queryset(self,request):
		if not hasattr(self, '_queryset'):
			self._queryset = Comment.objects.all()
		return self._queryset

	def has_delete_permission(self, request, obj=None):
		return False

class ProfileAdmin(admin.ModelAdmin):
	list_display = ('user',)
	search_fields = ('=user__username',)
	fields = ['avatar','banner','profile','location','hit_counter','old_password']
	raw_id_fields = ('user',)

	def has_add_permission(self, request, obj=None):
		return False

	def has_delete_permission(self, request, obj=None):
		return False

# Admin Registration

admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Profile,ProfileAdmin)

