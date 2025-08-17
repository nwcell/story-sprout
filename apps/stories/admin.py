from django.contrib import admin
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
    list_display = ("__str__", "user", "created_at")
    inlines = (PageInline,)


admin.site.register(Story, StoryAdmin)


class PageAdmin(OrderedModelAdmin):
    list_display = ("__str__", "story__user", "move_up_down_links")


admin.site.register(Page, PageAdmin)
