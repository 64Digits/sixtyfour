from rest_framework import viewsets, permissions
from .api_serializers import RecentPostSerializer
from rest_framework.response import Response
from .models import Post

"""
    Place Views responsible for returning serialized data here.
    The logic works much the same as normal queryset results, but we're not
    dealing with templates here, just plain data.
"""

class RecentActivity(viewsets.ReadOnlyModelViewSet):
	"""
	API endpoint for getting recent activity
	"""
	def list(self, request):
		user = self.request.user
		posts = Post.posts_recent(user).filter(show_recent=True)[:10]
		serializer = RecentPostSerializer(posts, many=True)
		return Response(serializer.data)