"""
	Serializers defined for rest framework responses
"""

from rest_framework import serializers
from .models import Post

class RecentPostSerializer(serializers.HyperlinkedModelSerializer):
	"""
		Serializes a limited subsection of fields from the Post model.
		Intended for use by the Recent Activity endpoint.
	"""
	user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
	class Meta:
		model = Post
		fields = ['interacted', 'updated', 'title', 'id', 'url', 'comments_count', 'user']

class PostSerializer(serializers.HyperlinkedModelSerializer):
	"""
		Serializes full post data for use by API endpoints.
	"""
	user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
	class Meta:
		model = Post
		fields = ['id', 'created', 'updated', 'interacted', 'url', 'title', 'entry', 'show_recent', 'pinned', 'locked', 'private', 'user', 'comments_count', 'visible_description']