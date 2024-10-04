from django.apps import AppConfig


class DjangoMailAnalyticsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_mail_analytics"

    def ready(self):
        # pylint: disable=import-outside-toplevel

        # monky patch mail functions
        from .mail import send

        _ = send  # just there to avoid autoremoval of the import
