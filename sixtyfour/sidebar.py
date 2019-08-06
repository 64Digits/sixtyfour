class Sidebar():
	name=""
	title=""

	@property
	def template(self):
		return ("sidebar/%s.html"%self.name)

	def with_context(self,context):
		return {}

class WithContext():
	context = {}

	def with_context(self,context):
		return {}

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context.update(self.context)
		context.update(self.with_context(context))
		return context

class WithSidebar(WithContext):
	sidebars = []

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		[context.update(s.with_context(context)) for s in self.sidebars]
		context.update({'sidebar':self.sidebars})
		return context

