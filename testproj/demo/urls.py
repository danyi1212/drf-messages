from django.urls import path

from demo import views

app_name = "demo"
urlpatterns = [
    path("", views.index, name="index"),
    path("blank/", views.blank, name="blank"),
    path("test/", views.test, name="test"),
]
