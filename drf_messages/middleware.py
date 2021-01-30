from drf_messages.models import Message


class ClearMessagesMiddleware:
    """
    Clear all seen messages after the request is finished.
    This middleware is not required because the messages will be deleted with
    the session at logout or on "clearsessions" command.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # delete all seen messages after request is done
        Message.objects.with_context(request).filter(seen_at__isnull=False).delete()
        return response
