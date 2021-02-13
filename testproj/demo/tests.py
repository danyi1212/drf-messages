from django.contrib import messages
from django.contrib.auth.models import User
from django.test import override_settings, TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from drf_messages.conf import MESSAGES_USE_SESSIONS, MESSAGES_DELETE_READ
from drf_messages.models import Message


class MessageDRFViewsTests(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user("testuser", password="secret")

    def login_session(self):
        self.client.force_login(self.user)

    @override_settings(MESSAGES_DELETE_READ=True)
    def test_message_expire(self):
        self.login_session()
        # create message
        response = self.client.get(reverse('demo:index'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # read message
        response = self.client.get(reverse("drf_messages:messages-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 1)
        # should delete previous message
        response = self.client.get(reverse("drf_messages:messages-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 1)

    def test_session_clear(self):
        self.login_session()
        # create message
        response = self.client.get(reverse('demo:index'))
        session_key = response.wsgi_request.session.session_key
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Message.objects.filter(session__session_key=session_key).count(), 1)
        # logout, clear session
        self.client.logout()
        self.assertEqual(Message.objects.filter(session__session_key=session_key).count(), 0)

    @override_settings(MESSAGES_USE_SESSIONS=True)
    def test_multi_session(self):
        # TODO settings not updating in conf.py
        self.login_session()
        # create message
        response = self.client.get(reverse('demo:index'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        session_key = response.wsgi_request.session.session_key
        self.assertEqual(Message.objects.filter(session__session_key=session_key).count(), 1)
        # read message
        response = self.client.get(reverse("drf_messages:messages-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data.get("results")), 1)
        # create new session
        new_client = Client()
        new_client.force_login(self.user)
        # read message
        response = new_client.get(reverse("drf_messages:messages-list"))
        session_key = response.wsgi_request.session.session_key
        self.assertEqual(Message.objects.filter(session__session_key=session_key).count(), 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("results"), [])

    def test_leave_message(self):
        text = "Leave a message"
        Message.objects.create_user_message(self.user, text, messages.INFO)
        self.login_session()
        response = self.client.get(reverse("drf_messages:messages-list"))
        self.assertEqual(response.data.get("results")[0].get("message"), text)


class MessageTests(TestCase):

    def test_create_message(self):
        user = User.objects.create_user("testuser", password="secret")
        message = Message.objects.create_user_message(user, "Hello world!", messages.WARNING, extra_tags="test")
        self.assertEqual(message.extra_tags.all().first().text, "test")
        message = Message.objects.create_user_message(user, "Hello world!", messages.WARNING,
                                                      extra_tags=["test1", "test2"])
        self.assertEqual(message.extra_tags.all().last().text, "test2")

    def test_add_message(self):
        # test message on unauthenticated request
        response = self.client.get(reverse("demo:test"))
        self.assertContains(response, "Hello world!")
