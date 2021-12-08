# pylint: disable=missing-function-docstring
from django.contrib import messages
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings


def index(request):
    messages.info(request, "Hello world!", extra_tags="test")
    return render(request, "demo/index.html")


def blank(request):
    return render(request, "demo/index.html")


@api_view(["GET"])
def test(request):
    messages.info(request, "Hello world!", extra_tags="test")
    return Response("Hello world!")
