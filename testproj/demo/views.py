# pylint: disable=missing-function-docstring
from django.contrib import messages
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def index(request):
    messages.info(request, "Hello world!", extra_tags="test")
    return Response("Hello world!")


def test(request):
    messages.info(request, "Hello world!", extra_tags="test")
    return render(request, "demo/index.html")
