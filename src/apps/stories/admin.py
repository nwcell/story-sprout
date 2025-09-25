from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from ordered_model.admin import OrderedInlineModelAdminMixin, OrderedModelAdmin, OrderedStackedInline

from .models import Page, Story


class PageInline(OrderedStackedInline):
    model = Page
    fields = (
        "content",
        "image_text",
        "image",
        "move_up_down_links",
    )
    readonly_fields = ("move_up_down_links",)
    ordering = ("order",)
    extra = 1


class StoryAdmin(OrderedInlineModelAdminMixin, admin.ModelAdmin):
    list_display = ("__str__", "uuid", "user", "conversation_link", "created_at")
    inlines = (PageInline,)

    @admin.display(description="Conversation", ordering="conversation__title")
    def conversation_link(self, obj):
        if not obj.conversation_id:
            return "-"
        url = reverse("admin:ai_conversation_change", args=[obj.conversation_id])
        title = obj.conversation.title or obj.conversation.uuid
        return format_html('<a href="{}">{}</a>', url, title)


admin.site.register(Story, StoryAdmin)


class PageAdmin(OrderedModelAdmin):
    list_display = ("__str__", "story__user", "move_up_down_links")


admin.site.register(Page, PageAdmin)
