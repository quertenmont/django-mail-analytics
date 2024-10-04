# import django.core.mail as mail
import logging
import re
from datetime import datetime
from functools import cache

import wrapt
from django.conf import settings
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
    if url.startswith(f"{scheme}://{domain}"):
        url = url.replace(f"{scheme}://{domain}", "")

    uri = reverse("mail_proxy")
    qp = urlencode({"q": get_hasher().encode(q), "u": url})
    return f"{scheme}://{domain}{uri}?{qp}"


def replace_href_by_proxy(q, href_match):
    url = href_match.group(1)
    proxy = get_proxy_url(q, url)
    return f'href="{proxy}"'


@wrapt.patch_function_wrapper("django.core.mail", "EmailMessage.send")
def send(wrapped, instance, args, kwargs):
    def get_mailId(instance, html_message, tracker):
        subject = instance.subject
        from_email = instance.from_email
        recipient_list = instance.recipients()

        mail, _ = Mail.objects.update_or_create(
            key=tracker or subject[:25],
            date=datetime.now().date(),
            create_defaults=dict(
                sender=from_email,
                subject=subject[:2048],
                body=html_message,
            ),
        )

        mailRecipient, _ = MailRecipient.objects.update_or_create(
            mail=mail, recipient=",".join(recipient_list)
        )
        return mail.id, mailRecipient.id

    mailId, mailRId = 0, 0

    # check for tracker code from email recipent list
    trackers = [x.rsplit("@", 1)[0] for x in instance.to if x.lower().endswith("@dma")]
    instance.to = [x for x in instance.to if not x.lower().endswith("@dma")]

    tracker = trackers[-1] if trackers else None
    if hasattr(instance, "alternatives"):
        for I, x in enumerate(instance.alternatives):
            alternative, mime_type = x
            if mime_type == "text/html" and alternative:
                html_message = alternative

                if not mailId or not mailRId:
                    mailId, mailRId = get_mailId(instance, html_message, tracker)

                if "</body>" in html_message:
                    html_message = html_message.replace(
                        "</body>", f"{get_pixel_tag(mailRId)}\n</body>"
                    )

                # check if there tags with href attributes and replace them by a proxy
                def sub_replacor(href_match, mailRId=mailRId):
                    return replace_href_by_proxy(mailRId, href_match)

                html_message, _ = re.subn(
                    '''href="(.*?)"''', sub_replacor, html_message
                )

                instance.alternatives[I] = (html_message, mime_type)

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
