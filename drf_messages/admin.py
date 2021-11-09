from django.contrib import admin
from django import forms
from django.contrib.messages.storage.base import LEVEL_TAGS

from drf_messages.models import Message, MessageTag


class MessageAdminForm(forms.ModelForm):
    level = forms.ChoiceField(choices=LEVEL_TAGS.items())

    class Meta:
        model = Message
        fields = "__all__"


class MessageTagInline(admin.StackedInline):
    model = MessageTag
    fields = ("text",)
    extra = 0


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    form = MessageAdminForm
    list_display = ("session", "message", "level_tag", "read_at")
    list_filter = ("created", "extra_tags", "level", "read_at", "view", "session")
    readonly_fields = ("session", "created")

    inlines = (MessageTagInline,)
