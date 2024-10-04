[![](https://img.shields.io/pypi/pyversions/django-mail-analytics.svg?color=3776AB&logo=python&logoColor=white)](https://www.python.org/)
[![](https://img.shields.io/pypi/djversions/django-mail-analytics?color=0C4B33&logo=django&logoColor=white&label=django)](https://www.djangoproject.com/)

[![](https://img.shields.io/pypi/v/django-mail-analytics.svg?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/django-mail-analytics/)
[![](https://static.pepy.tech/badge/django-mail-analytics/month)](https://pepy.tech/project/django-mail-analytics)
[![](https://img.shields.io/github/stars/quertenmont/django-mail-analytics?logo=github&style=flat)](https://github.com/quertenmont/django-mail-analytics/stargazers)
[![](https://img.shields.io/pypi/l/django-mail-analytics.svg?color=blue)](https://github.com/quertenmont/django-mail-analytics/blob/main/LICENSE.txt)

[![](https://results.pre-commit.ci/badge/github/quertenmont/django-mail-analytics/main.svg)](https://results.pre-commit.ci/latest/github/quertenmont/django-mail-analytics/main)
[![](https://img.shields.io/github/actions/workflow/status/quertenmont/django-mail-analytics/test-package.yml?branch=main&label=build&logo=github)](https://github.com/quertenmont/django-mail-analytics)
[![](https://img.shields.io/codecov/c/gh/quertenmont/django-mail-analytics?logo=codecov)](https://codecov.io/gh/quertenmont/django-mail-analytics)
[![](https://img.shields.io/codacy/grade/194566618f424a819ce43450ea0af081?logo=codacy)](https://www.codacy.com/app/quertenmont/django-mail-analytics)
[![](https://img.shields.io/badge/code%20style-black-000000.svg?logo=python&logoColor=black)](https://github.com/psf/black)
[![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)



# django-mail-analytics

Simple python module that add email tracking features for both mail opening (via a hidden pixel) and for link clicks (via a redirecting proxy)
-  This works only for email with an html body
-  The changes to your code is minimal as we monkey patch the standard django.core.mail.EmailMessage object
-  Three new models are added to save mail sent, mail recipients and mail recipient's action such as opening and link clicking

---

## Installation
-   Run `pip install django-mail-analytics`
-   Add `django_mail_analytics` to your installed INSTALLED_APPS
-   Add `re_path(r"^m/", include("django_mail_analytics.urls"))` to your urls
-   Add this to your settings:
```
MAIL_ANALYTICS = {
    "DOMAIN": "localhost", #add the domain of your app to be used in the pixel/proxy url of your mail sent
    "SCHEME": "http", #http or https
  # "SALT": "my-salt", #comment to use global SECRET_KEY instead
    "LENGTH": 6,  # minimal length of encoded id
}
```

---

## Usage

All email sent with an html body will be modified on the fly to incorporate a pixel tracking and to rewrite link urls:

```
from django.core.mail import send_mail

send_mail(
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
```
The above code will actually send an html body email that is rewritten like this:
```
<body>
    <a href="http://localhost/m/p?q=OJe2wr&u=https%3A%2F%2Fgoogle.com">link</a>
    <img src="http://localhost/m/i?q=OJe2wr" height="0px" width="0px"/>
</body>
```
There is no perciple change for the user that receive the email.
But as soon as it opens (or reopens) the email, we create a MailRecipientAction with an empty action.
If the user clicks on the link we would create another MailRecipientAction with an action equal to the link url: "https://google.com" in this example.


Every email send trigger the creation of a Mail object.
In addition, a MailRecipient object is also created for every recipients of the email.

Note, that multiple emails sharing the same "key" and sending "date" are merged together into a single Mail Object.
So no need to worry about sending mass emails (they will only create one single Mail object).
The email "key" is either the email subject OR the first recipient with a "@DMA" email address.  This recipient is ignored from the sending list, it's just an easy way to track mails of a given category.

So typical usage is like this:
```
send_mail(
    subject="subject",
    message="message",
    html_message="html_message,
    from_email=None,
    recipient_list=[user.email, f"EMAIL_KEY@DMA"],
)
```

---

## Admin

There is a django admin for the three added models that can easilly be used to monitor your email success rate and typical use behaviour.

---

## Remarks

Email were not developped for tracking in the first place.
So adding a pixel tracking and link proxy is just a workaround to add tracking capabilities to email.
One of the limitation of this workaround is that sending the email to multiple recipients doesn't allow to distinguish who among the recipients is currently opening the email... just that someone did it.
Similarly if the email is forwarded to somebody else, we can only know that the email was opened a second time, but not that it's from a different people.

---

## Testing
```bash
# clone repository
git clone https://github.com/quertenmont/django-mail-analytics.git && cd django_mail_analytics

# create virtualenv and activate it
python -m venv venv && . venv/bin/activate

# upgrade pip
python -m pip install --upgrade pip

# install requirements
pip install -r requirements.txt -r requirements-test.txt

# install pre-commit to run formatters and linters
pre-commit install --install-hooks

# run tests
tox
# or
python runtests.py
# or
python -m django test --settings "tests.settings"
```
---

## License
Released under [MIT License](LICENSE.txt).

---

## Supporting

- :star: Star this project on [GitHub](https://github.com/quertenmont/django-mail-analytics)
- :octocat: Follow me on [GitHub](https://github.com/quertenmont)
- :blue_heart: Follow me on [Twitter](https://twitter.com/LoicQuertenmont)
- :moneybag: Sponsor me on [Github](https://github.com/sponsors/quertenmont)
