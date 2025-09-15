from mcp_server import ModelQueryToolset

from apps.stories.models import Story


class StoryTool(ModelQueryToolset):
    model = Story

    def get_queryset(self):
        """self.request can be used to filter the queryset"""
        return super().get_queryset().filter(user=self.request.user)
