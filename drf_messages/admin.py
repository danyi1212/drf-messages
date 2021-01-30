from django.contrib import admin

from drf_messages.models import Message, MessageTag


class MessageTagInline(admin.StackedInline):
    model = MessageTag
    fields = ("text",)
    extra = 0


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("session", "message", "level_tag", "seen_at")
    list_filter = ("created", "extra_tags", "level", "seen_at", "view", "session")
    readonly_fields = ("session", "created")

    inlines = (MessageTagInline,)

