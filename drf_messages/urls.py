from rest_framework.routers import DefaultRouter

from drf_messages.views import MessagesViewSet

router = DefaultRouter()
router.register("", MessagesViewSet, "messages")


app_name = "drf_messages"
urlpatterns = [
    *router.urls,
]
