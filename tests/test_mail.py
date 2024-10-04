import math
import re
from datetime import datetime, timezone

from django.contrib.auth.models import Group, User
from django.core import mail
from django.db.models.base import ModelBase
from django.test import Client, TestCase
from django.urls import reverse

from django_mail_analytics.models import Mail, MailRecipient, MailRecipientAction


def get_admin_change_view_url(obj: object) -> str:
    return reverse(
        "admin:{}_{}_change".format(obj._meta.app_label, type(obj).__name__.lower()),
        args=(obj.pk,),
    )


def get_admin_list_view_url(model: ModelBase) -> str:
    return reverse(
        "admin:{}_{}_changelist".format(model._meta.app_label, model.__name__.lower()),
    )


class MailTestCase(TestCase):
    def setUp(self):
        mail.send_mail(
            "Subject here",
            "Here is the message.",
            "from@example.com",
            ["to@example.com"],
            fail_silently=False,
            html_message="""
            <body>
            <a href="https://google.com">link</a>
            </body>
            """,
        )

    def tearDown(self):
        mail.outbox = []

    def get_html_body(self):
        # Get modified HTML body
        html_body: str = getattr(mail.outbox[0], "alternatives", [("", None)])[0][0]
        return html_body

    def populate_db(self):
        mail = Mail(
            key="KEY",
            date=datetime.now(),
            sender="from@example.com",
            subject="subject",
            body="body",
        )
        mail.save()

        recipient = MailRecipient(mail=mail, recipient="to@example.com")
        recipient.save()

        action = MailRecipientAction(recipient=recipient, action="")
        action.save()

    def test_outbox(self):
        """
        Checking that there is indeed a mail in the outbox
        """
        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertEqual(mail.outbox[0].subject, "Subject here")

    def test_mail_pixel(self):
        """
        Checking that there is a pixel link associated to the email and that it returns a pixel
        """
        c = Client()

        match = re.search('<img src="(.*?)"', self.get_html_body())
        self.assertIsNotNone(match)
        if match:
            pixel_link = match.group(1)
            pixel_link = pixel_link.replace("http://localhost", "", 1)
            response = c.get(pixel_link)
            self.assertEqual(response.status_code, 200)

        # verify that we have registered an action
        qs = MailRecipientAction.objects.filter(action="")
        self.assertEqual(qs.count(), 1)

        # verify that the link is properly registed
        q = qs.first()
        self.assertIsNotNone(q)
        if q:
            self.assertEqual(q.action, "")
            self.assertEqual(q.recipient.recipient, "to@example.com")
            self.assertEqual(q.recipient.mail.sender, "from@example.com")

    def test_mail_link(self):
        """
        Checking that there is a wrapper around email links
        """
        c = Client()

        match = re.search('<a href="(.*?)"', self.get_html_body())
        self.assertIsNotNone(match)
        if match:
            link = match.group(1)
            link = link.replace("http://localhost", "", 1)
            response = c.get(link)
            self.assertEqual(response.status_code, 302)

        # verify that we have registered an action
        qs = MailRecipientAction.objects.exclude(action="")
        self.assertEqual(qs.count(), 1)

        # verify that the link is properly registed
        q = qs.first()
        self.assertIsNotNone(q)
        if q:
            self.assertEqual(q.action, "https://google.com")
            self.assertEqual(q.recipient.recipient, "to@example.com")
            self.assertEqual(q.recipient.mail.sender, "from@example.com")

            # call models str to increase code coverage
            _ = f"{q}, {q.recipient}, {q.recipient.mail}"

    def test_admin_views(self):
        self.populate_db()

        # create user an login
        User.objects.create_superuser(
            username="superuser", password="secret", email="admin@example.com"
        )
        c = Client()
        c.login(username="superuser", password="secret")

        # check the list and change view of Mail
        mail = Mail.objects.first()
        response = c.get(get_admin_list_view_url(Mail))
        self.assertEqual(response.status_code, 200)
        response = c.get(get_admin_change_view_url(mail))
        self.assertEqual(response.status_code, 200)

        # check the list and change view of MailRecipient
        recipient = MailRecipient.objects.first()
        response = c.get(get_admin_list_view_url(MailRecipient))
        self.assertEqual(response.status_code, 200)
        response = c.get(get_admin_change_view_url(recipient))
        self.assertEqual(response.status_code, 200)

        # check the list and change view of MailRecipientAction
        action = MailRecipientAction.objects.first()
        response = c.get(get_admin_list_view_url(MailRecipientAction))
        self.assertEqual(response.status_code, 200)
        response = c.get(get_admin_change_view_url(action))
        self.assertEqual(response.status_code, 200)

    def test_list_view(self):
        self.populate_db()

        # create user an login
        User.objects.create_superuser(
            username="superuser", password="secret", email="admin@example.com"
        )
        c = Client()
        c.login(username="superuser", password="secret")

        response = c.get(reverse("mail_list"))
        self.assertEqual(response.status_code, 200)
