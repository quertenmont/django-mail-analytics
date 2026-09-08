# import django.core.mail as mail
import logging
import re
from datetime import datetime
from functools import cache

import wrapt
from django.conf import settings
from django.core.mail.message import EmailAlternative as _EmailAlternative
from django.urls import reverse
from django.utils.http import urlencode
from hashids import Hashids

from .models import Mail, MailRecipient, MailRecipientAction

logger = logging.getLogger(__name__)


@cache
def mail_settings() -> dict:
    default_settings = getattr(settings, "MAIL_ANALYTICS", {})
    if "SALT" not in default_settings:
        default_settings["SALT"] = getattr(settings, "SECRET_KEY", "salt")
    if "LENGTH" not in default_settings:
        default_settings["LENGTH"] = 6
    if "ENABLED" not in default_settings:
        default_settings["ENABLED"] = True
    return default_settings


@cache
def get_hasher():
    salt = mail_settings()["SALT"]
    length = mail_settings()["LENGTH"]
    return Hashids(salt=salt, min_length=length)


def get_pixel_tag(q):
    scheme = mail_settings()["SCHEME"]
    domain = mail_settings()["DOMAIN"]
    uri = reverse("mail_pixel")
    qp = urlencode({"q": get_hasher().encode(q)})
    url = f"{scheme}://{domain}{uri}?{qp}"
    return f"""<img src="{url}" height="0px" width="0px"/>"""


def get_proxy_url(q, url):
    scheme = mail_settings()["SCHEME"]
    domain = mail_settings()["DOMAIN"]

    uri = reverse("mail_proxy")
    qp = urlencode({"q": get_hasher().encode(q), "u": url})
    return f"{scheme}://{domain}{uri}?{qp}"


def replace_href_by_proxy(q, href_match):
    url = href_match.group(1)
    proxy = get_proxy_url(q, url)
    return f'href="{proxy}"'


def _get_mail_id(instance, html_message, tracker):
    subject = instance.subject
    from_email = instance.from_email
    recipient_list = instance.recipients()

    try:
        mail, _ = Mail.objects.update_or_create(
            key=tracker or subject[:25],
            date=datetime.now().date(),
            create_defaults={
                "sender": from_email,
                "subject": subject[:2048],
                "body": html_message,
            },
        )
    except Mail.MultipleObjectsReturned:
        mail = Mail.objects.filter(
            key=tracker or subject[:25],
            date=datetime.now().date(),
        ).first()

    try:
        mail_recipient, _ = MailRecipient.objects.update_or_create(
            mail=mail, recipient=",".join(recipient_list)
        )
    except MailRecipient.MultipleObjectsReturned:
        mail_recipient = MailRecipient.objects.filter(
            mail=mail, recipient=",".join(recipient_list)
        ).first()

    return mail.id, mail_recipient.id


def _inject_tracking(instance, tracker):
    mail_id, mail_r_id = 0, 0
    for alt_i, x in enumerate(instance.alternatives):
        alternative, mime_type = x
        if mime_type == "text/html" and alternative:
            html_message = alternative

            if not mail_id or not mail_r_id:
                mail_id, mail_r_id = _get_mail_id(instance, html_message, tracker)

            if "</body>" in html_message:
                html_message = html_message.replace(
                    "</body>", f"{get_pixel_tag(mail_r_id)}\n</body>"
                )

            # check if there tags with href attributes and replace them by a proxy
            def sub_replacor(href_match, mail_r_id=mail_r_id):
                return replace_href_by_proxy(mail_r_id, href_match)

            html_message, _ = re.subn('''href="(.*?)"''', sub_replacor, html_message)

            instance.alternatives[alt_i] = _EmailAlternative(html_message, mime_type)


@wrapt.patch_function_wrapper("django.core.mail", "EmailMessage.send")
def send(wrapped, instance, args, kwargs):
    # check for tracker code from email recipent list
    trackers = [x.rsplit("@", 1)[0] for x in instance.to if x.lower().endswith("@dma")]
    instance.to = [x for x in instance.to if not x.lower().endswith("@dma")]

    tracker = trackers[-1] if trackers else None
    if mail_settings().get("ENABLED", True):
        try:
            if hasattr(instance, "alternatives"):
                _inject_tracking(instance, tracker)
        except Exception:
            logger.exception(
                "Failed to track email analytics; sending email without tracking"
            )

    return wrapped(*args, **kwargs)


async def register_action(q, url=""):
    if q is None:
        return

    try:
        # decode query
        decoded = get_hasher().decode(q)
        assert decoded
        q = decoded[0]

        exists = await MailRecipient.objects.filter(id=q).aexists()
        if not exists:
            logging.warning(f"ignoring unexistant recipient_id {q}")
            return

        await MailRecipientAction.objects.acreate(recipient_id=q, action=url)

    except Exception as e:
        logging.error("ERROR", type(e), e.__dict__)
