# pylint: disable=missing-function-docstring, protected-access, no-member, not-context-manager
from django.contrib import messages
from django.contrib.messages import get_messages, set_level
from django.contrib.messages.storage.base import Message as DjangoMessage
from django.test import override_settings, modify_settings, TestCase, TransactionTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from demo.factories import MessageFactory
from demo.user_factories import UserFactory
from drf_messages.models import Message
from drf_messages.storage import DBStorage


class MessageDRFViewsTests(APITestCase):
    user = None
    message = None

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.message = MessageFactory(user=cls.user)

    def setUp(self):
        self.client.force_login(self.user)

    def test_read_message_list(self):
        Message.objects.bulk_create(MessageFactory.build(user=self.user) for _ in range(19))

        response = self.client.get(reverse("drf_messages:messages-list"), dict(unread=True))
        self.assertEqual(response.data.get("count"), 20)
        self.assertEqual(len(response.data.get("results")), 10)
        read_messages_ids = {m.get("id") for m in response.data.get("results")}
        # verify 10 messages marked read and not returned twice
        response = self.client.get(reverse("drf_messages:messages-list"), dict(unread=True))
        self.assertEqual(response.data.get("count"), 10)
        self.assertEqual(len(response.data.get("results")), 10)
        self.assertNotEqual(
            read_messages_ids, {m.get("id") for m in response.data.get("results")}
        )

        # make sure no messages left
        response = self.client.get(reverse("drf_messages:messages-list"), dict(unread=True))
        self.assertEqual(response.data.get("count"), 0)

    def test_read_message_detail(self):
        response = self.client.get(reverse("drf_messages:messages-detail", kwargs=dict(pk=self.message.pk)))
        self.assertEqual(response.data.get("message"), self.message.message)
        self.assertEqual(response.data.get("level"), self.message.level)
        self.assertEqual(response.data.get("level_tag"), self.message.level_tag)
        self.assertEqual(response.data.get("view"), self.message.view)
        self.assertEqual(response.data.get("extra_tags"), list(self.message.extra_tags.values_list("text", flat=True)))
        self.assertTrue(response.data.get("created"))
        self.assertEqual(response.data.get("read_at"), None)
        self.message.refresh_from_db()
        self.assertTrue(self.message.read_at, msg="Message did not update read_at after reading through the API")

    def test_peak_messages(self):
        # peek messages
        response = self.client.get(reverse('drf_messages:messages-peek'))
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        self.assertEqual(response.data, dict(
            count=1,
            max_level=self.message.level,
            max_level_tag=self.message.level_tag,
        ))
        # create higher level message
        Message.objects.create_user_message(self.user, "warning message", messages.ERROR)
        # peek again
        response = self.client.get(reverse('drf_messages:messages-peek'))
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        self.assertEqual(response.data, dict(
            count=2,
            max_level=40,
            max_level_tag="error",
        ))

    @override_settings(MESSAGES_DELETE_READ=True)
    def test_message_expire(self):
        # read message
        response = self.client.get(reverse("drf_messages:messages-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        self.assertEqual(len(response.data.get("results")), 1)
        self.assertFalse(Message.objects.filter(user=self.user).exists())

    @override_settings(MESSAGE_STORAGE='django.contrib.messages.storage.fallback.FallbackStorage', DEBUG=False)
    def test_incorrect_storage_backend(self):
        self.assertRaises(ValueError, self.client.get, (reverse("drf_messages:messages-list")))

    @override_settings(MESSAGES_ALLOW_DELETE_UNREAD=False)
    def test_delete_unread_messages(self):
        # delete before read
        response = self.client.delete(reverse("drf_messages:messages-detail", kwargs=dict(pk=self.message.pk)))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, msg=response.data)
        # read message
        response = self.client.get(reverse("drf_messages:messages-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        # delete after read
        response = self.client.delete(reverse("drf_messages:messages-detail", kwargs=dict(pk=self.message.pk)))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, msg=response.data)

    @override_settings(MESSAGES_ALLOW_DELETE_UNREAD=True)
    def test_delete_unread_messages_alt(self):
        # delete after read
        response = self.client.delete(reverse("drf_messages:messages-detail", kwargs=dict(pk=self.message.pk)))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, msg=response.data)


class MessageTestCase(TransactionTestCase):

    def setUp(self):
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.response = self.client.get(reverse('demo:index'))
        self.request = self.response.wsgi_request

    def test_create_info_message(self):
        messages.info(self.request, "Hello world!")
        message = Message.objects.with_context(self.request).first()
        self.assertEqual(message.level, 20)
        self.assertEqual(message.level_tag, "info")

    @override_settings(MESSAGE_TAGS={
        10: 'debug',
        20: 'info',
        25: 'success',
        30: 'warning',
        40: 'error',
        50: 'critical',
    })
    def test_create_critical_message(self):
        messages.add_message(self.request, 50, "Hello world!")
        message = Message.objects.with_context(self.request).first()
        self.assertEqual(message.level, 50)
        self.assertEqual(message.level_tag, "")  # not updated due to issue https://code.djangoproject.com/ticket/33303

    def test_create_unknown_message(self):
        messages.add_message(self.request, 100, "Hello world!")
        message = Message.objects.with_context(self.request).first()
        self.assertEqual(message.level, 100)
        self.assertEqual(message.level_tag, "")

    def test_skip_message_level(self):
        Message.objects.all().delete()  # Clear all messages
        set_level(self.request, messages.WARNING)  # Update minimum level

        # Skip due to level too low
        with self.assertLogs('drf_messages', level="DEBUG") as logs:
            messages.info(self.request, "Hello world!")
            self.assertEqual(Message.objects.count(), 0)
            self.assertEqual(logs.records[0].levelname, "DEBUG")
            self.assertEqual(logs.records[0].module, "storage")
            self.assertEqual(
                logs.records[0].message,
                'Skip message creation due to the level being too low (level=20 / min=30).',
            )

        # Don't skip when level match
        messages.warning(self.request, "Hello world!")
        self.assertEqual(Message.objects.count(), 1)
        message = Message.objects.with_context(self.request).first()
        self.assertEqual(message.level, 30)
        self.assertEqual(message.level_tag, "warning")

    def test_skip_message_empty(self):
        Message.objects.all().delete()  # Clear all messages

        # Skip due to empty message
        with self.assertLogs('drf_messages', level="DEBUG") as logs:
            messages.info(self.request, "")
            self.assertEqual(Message.objects.count(), 0)
            self.assertEqual(logs.records[0].levelname, "DEBUG")
            self.assertEqual(logs.records[0].module, "storage")
            self.assertEqual(logs.records[0].message, "Skip message creation due to an empty string. (message='')")

    def test_extra_tags(self):
        messages.info(self.request, "Hello world", extra_tags=["test1", "test2"])
        storage: DBStorage = get_messages(self.request)
        message = list(storage)[0]
        self.assertEqual(message.extra_tags, "test1 test2")


class StorageTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.alt_client = cls.client_class()
        cls.anon_client = cls.client_class()

    def setUp(self):
        self.client.force_login(self.user)
        self.response = self.client.get(reverse('demo:test'))
        self.request = self.response.wsgi_request

        self.alt_client.force_login(self.user)

    def test_inside_template(self):
        response = self.client.get(reverse("demo:index"))
        storage: DBStorage = get_messages(response.wsgi_request)
        self.assertContains(response, "Hello world!")
        self.assertFalse(storage)
        self.assertTrue(storage.used)

    @override_settings(MESSAGES_USE_SESSIONS=True)
    def test_first_session(self):
        # check from database
        session_key = self.client.session.session_key
        self.assertEqual(Message.objects.filter(session__session_key=session_key).count(), 1)
        # check through storage
        storage: DBStorage = get_messages(self.request)
        self.assertEqual(len(storage), 1)
        # check through API
        response = self.client.get(reverse("drf_messages:messages-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        self.assertEqual(len(response.data.get("results")), 1)

    @override_settings(MESSAGES_USE_SESSIONS=True)
    def test_alt_session(self):
        # check API from different session
        response = self.alt_client.get(reverse("drf_messages:messages-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        self.assertEqual(len(response.data.get("results")), 0)
        # check from database using different session
        session_key = self.alt_client.session.session_key
        self.assertEqual(Message.objects.filter(session__session_key=session_key).count(), 0)
        # check storage for different session
        alt_storage: DBStorage = get_messages(response.wsgi_request)
        alt_storage.get_queryset().update(read_at=None)  # unread all messages
        self.assertEqual(len(alt_storage), 0)
        self.assertFalse(alt_storage)

    @override_settings(MESSAGES_USE_SESSIONS=False)
    def test_without_sessions(self):
        # check alt through API
        response = self.alt_client.get(reverse("drf_messages:messages-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK, msg=response.data)
        self.assertEqual(len(response.data.get("results")), 1)
        # check storage for different session
        alt_storage: DBStorage = get_messages(response.wsgi_request)
        alt_storage.get_queryset().update(read_at=None)  # unread all messages
        self.assertEqual(len(alt_storage), 1)
        self.assertTrue(alt_storage)

    def test_iteration(self):
        storage: DBStorage = get_messages(self.request)
        for message in storage:
            self.assertTrue(isinstance(message, DjangoMessage))

        self.assertEqual(len(storage), 0)
        self.assertTrue(storage.used)

    def test_with_operator(self):
        # read messages inside "with"
        with get_messages(self.request) as storage:
            self.assertEqual(storage.get_queryset().count(), 1)

        # check all messages marked read
        storage: DBStorage = get_messages(self.request)
        self.assertEqual(storage.get_unread_queryset().count(), 0)

    def test_print_messages(self):
        storage: DBStorage = get_messages(self.request)
        self.assertEqual(repr(storage), str(["Hello world!"]))
        self.assertFalse(storage.used)

    @override_settings(MESSAGES_USE_SESSIONS=False)
    def test_slicing(self):
        Message.objects.bulk_create(MessageFactory.build(user=self.user) for _ in range(9))
        storage: DBStorage = get_messages(self.request)
        self.assertEqual(len(storage), 10)
        self.assertEqual(len(storage[:5]), 5)
        self.assertEqual(len(storage), 5, msg="Messages not marked as read after slicing")
        self.assertTrue(storage.used)

    def test_contains(self):
        message = Message.objects.get(user=self.user)
        storage: DBStorage = get_messages(self.request)
        self.assertTrue(message.get_django_message() in storage)
        self.assertFalse(storage.used)


class StorageFallbackTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.alt_client = cls.client_class()
        cls.anon_client = cls.client_class()

    def setUp(self):
        self.response = self.anon_client.get(reverse('demo:index'))
        self.request = self.response.wsgi_request

        self.alt_client.force_login(self.user)

    @modify_settings(MIDDLEWARE={"remove": [
        "django.contrib.sessions.middleware.SessionMiddleware",
        'django.contrib.auth.middleware.AuthenticationMiddleware',
    ]})
    @override_settings(MESSAGES_USE_SESSIONS=True)
    def test_with_sessions(self):
        # refresh request / response after middleware removal
        client = self.client_class()
        self.response = client.get(reverse('demo:index'))
        self.request = self.response.wsgi_request
        self.assertFalse(hasattr(self.request, "session"))

        storage: DBStorage = get_messages(self.request)
        self.assertTrue(storage._fallback)
        self.assertEqual(len(storage), 1)
        self.assertTrue(storage)
        self.assertEqual(storage.get_queryset().count(), 0)

    def test_inside_template(self):
        storage: DBStorage = get_messages(self.request)
        self.assertTrue(storage._fallback)
        self.assertContains(self.response, storage[0].message)

    @override_settings(MESSAGES_USE_SESSIONS=False)
    def test_without_sessions(self):
        storage: DBStorage = get_messages(self.request)
        self.assertTrue(storage._fallback)
        self.assertEqual(len(storage), 1)
        self.assertTrue(storage)
        self.assertEqual(storage.get_queryset().count(), 0)

    def test_iteration(self):
        storage: DBStorage = get_messages(self.request)
        for message in storage:
            self.assertTrue(isinstance(message, DjangoMessage))

        self.assertTrue(storage.used)

    def test_contains(self):
        storage: DBStorage = get_messages(self.request)
        self.assertTrue(storage[0] in storage)

    def test_print_messages(self):
        storage: DBStorage = get_messages(self.request)
        self.assertEqual(repr(storage), str(["Hello world!"]))
        self.assertFalse(storage.used)


class MessageModelTestCase(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.client.force_login(self.user)
        self.response = self.client.get(reverse('demo:index'))
        self.request = self.response.wsgi_request
        self.session_key = self.client.session.session_key
        self.message = Message.objects.get(user=self.user)

    def test_created_message_view(self):
        self.assertEqual(self.message.view, "demo:index")

    def test_message_session(self):
        self.assertEqual(Message.objects.filter(session__session_key=self.session_key).count(), 1)

    def test_session_clear_on_logout(self):
        self.client.logout()
        self.assertEqual(Message.objects.filter(session__session_key=self.session_key).count(), 0)
        self.client.force_login(self.user)

    @modify_settings(MIDDLEWARE={"remove": "django.contrib.messages.middleware.MessageMiddleware"})
    @override_settings(MESSAGES_USE_SESSIONS=False)
    def test_missing_middleware(self):
        # refresh request / response after middleware removal
        client = self.client_class()
        client.force_login(user=self.user)
        self.response = client.get(reverse('demo:blank'))
        self.request = self.response.wsgi_request
        self.session_key = self.client.session.session_key
        self.assertFalse(hasattr(self.request, "_messages"))

        # create messages
        Message.objects.bulk_create(MessageFactory.build(user=self.user) for _ in range(10))

        with self.assertLogs("drf_messages") as logs:
            Message.objects.with_context(self.request).mark_read()
            self.message.mark_read(self.request)

        self.assertEqual(len(logs.records), 2)
        for entry in logs.records:
            self.assertEqual(entry.levelname, "ERROR")
            self.assertTrue("django.contrib.messages.middleware.MessageMiddleware" in entry.message)

    def test_parse_django_message(self):
        django_message = self.message.get_django_message()
        self.assertEqual(django_message.message, "Hello world!")
        self.assertEqual(django_message.level, messages.INFO)
        self.assertEqual(django_message.extra_tags, "test")
        self.assertEqual(django_message.tags, "test info")

    def test_parse_django_message_extra_tags(self):
        self.message.add_tag(f"tag{i}" for i in range(3))
        django_message = self.message.get_django_message()
        self.assertEqual(django_message.extra_tags, "test tag0 tag1 tag2")
        self.assertEqual(django_message.tags, "test tag0 tag1 tag2 info")
