from django.urls import path

from demo import views

app_name = "demo"
urlpatterns = [
    path("", views.index, name="index"),
    path("test/", views.test, name="test"),
]
