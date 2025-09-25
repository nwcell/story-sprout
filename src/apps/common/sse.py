from django.template.loader import render_to_string
from django_eventstream import send_event
from django_eventstream.channelmanager import DefaultChannelManager

from apps.stories.models import Story


class ChannelManager(DefaultChannelManager):
    def can_read_channel(self, user, channel, request=None):
        # allow "user-<id>" channels
        if channel.startswith("user-"):
            return bool(user and user.is_authenticated and channel.startswith(f"user-{user.id}"))
        # allow "story-<story_uuid>" channels
        elif channel.startswith("story-"):
            # Extract UUID from channel name (everything after "story-")
            story_uuid = channel[6:]  # Remove "story-" prefix
            story = Story.objects.filter(uuid=story_uuid, user=user).first()
            return bool(user and user.is_authenticated and story)
        return False


def send_template(channel, event, template, context):
    rendered = render_to_string(template, context)
    send_event(channel, event, rendered, json_encode=False)


def send_oob(channel, template: str, context: dict | None = None):
    context = context if context else {}
    context["oob"] = True
    send_template(channel, "oob", template, context)


def update_element(channel, event, template, context):
    send_event(channel, event, "")
