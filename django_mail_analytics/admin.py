from django.contrib import admin
from django.db.models import Count, Q
from django.utils.safestring import mark_safe

from .models import Mail, MailRecipient, MailRecipientAction


class MailRecipientActionInline(admin.TabularInline):
    model = MailRecipientAction
    fields = ("pk", "created", "action")
    readonly_fields = ("pk", "created", "action")
    can_delete = False
    extra = 0
    max_num = 0
    show_change_link = True


@admin.register(MailRecipientAction)
class MailRecipientActionAdmin(admin.ModelAdmin):
    """Define admin model for MailRecipientAction model."""

    list_display = ("id", "created", "action", "recipient_email", "recipient_mail_key")
    readonly_fields = ("id", "created", "recipient", "action")


class MailRecipientInline(admin.TabularInline):
    model = MailRecipient
    fields = ("pk", "created", "email", "sent", "opened", "openings", "clicks")
    readonly_fields = ("pk", "created", "email", "sent", "opened", "openings", "clicks")
    can_delete = False
    extra = 0
    max_num = 0
    show_change_link = True

    def get_queryset(self, request):
        opening = Q(actions__action="")
        hasAction = Q(actions__isnull=False)
        qs = super().get_queryset(request)
        qs = qs.annotate(opened=Count("id", filter=hasAction & opening, distinct=True))
        qs = qs.annotate(sent=Count("id", distinct=True))
        qs = qs.annotate(openings=Count("actions", filter=opening))
        qs = qs.annotate(clicks=Count("actions", filter=~opening))
        return qs

    @admin.display(description="Opened")
    def opened(self, instance):
        return instance.opened

    @admin.display(description="Sent")
    def sent(self, instance):
        return instance.sent

    @admin.display(description="Openings")
    def openings(self, instance):
        return instance.openings

    @admin.display(description="Clicks")
    def clicks(self, instance):
        return instance.clicks


@admin.register(MailRecipient)
class MailRecipientAdmin(admin.ModelAdmin):
    """Define admin model for MailRecipient model."""

    def get_queryset(self, request):
        opening = Q(actions__action="")
        hasAction = Q(actions__isnull=False)

        qs = super().get_queryset(request)
        qs = qs.annotate(opened=Count("id", filter=hasAction & opening, distinct=True))
        qs = qs.annotate(sent=Count("id", distinct=True))
        qs = qs.annotate(openings=Count("actions", filter=opening))
        qs = qs.annotate(clicks=Count("actions", filter=~opening))
        return qs

    @admin.display(description="Success Rate")
    def rate(self, instance):
        return f"{int(100*(instance.opened/instance.sent))}%"

    @admin.display(description="Opened")
    def opened(self, instance):
        return instance.opened

    @admin.display(description="Sent")
    def sent(self, instance):
        return instance.sent

    @admin.display(description="Openings")
    def openings(self, instance):
        return instance.openings

    @admin.display(description="Clicks")
    def clicks(self, instance):
        return instance.clicks

    list_display = ("id", "created", "mail_key", "email", "rate", "opened", "sent", "openings", "clicks")
    readonly_fields = (
        "id",
        "mail",
        "recipient",
    )
    inlines = [
        MailRecipientActionInline,
    ]


@admin.register(Mail)
class MailAdmin(admin.ModelAdmin):
    """Define admin model for Mail model."""

    def get_queryset(self, request):
        opening = Q(recipients__actions__action="")
        hasAction = Q(recipients__actions__isnull=False)

        qs = super().get_queryset(request)
        qs = qs.annotate(opened=Count("recipients", filter=hasAction & opening, distinct=True))
        qs = qs.annotate(sent=Count("recipients", distinct=True))
        qs = qs.annotate(openings=Count("recipients__actions", filter=opening))
        qs = qs.annotate(clicks=Count("recipients__actions", filter=~opening))
        return qs

    def body_html(self, obj):
        return mark_safe(obj.body)

    @admin.display(description="Success Rate")
    def rate(self, instance):
        return f"{int(100*(instance.opened/instance.sent))}%"

    @admin.display(description="Opened")
    def opened(self, instance):
        return instance.opened

    @admin.display(description="Sent")
    def sent(self, instance):
        return instance.sent

    @admin.display(description="Openings")
    def openings(self, instance):
        return instance.openings

    @admin.display(description="Clicks")
    def clicks(self, instance):
        return instance.clicks

    exclude = ("body",)
    readonly_fields = (
        "id",
        "key",
        "sender",
        "subject",
        "body_html",
    )

    list_display = ("id", "created", "key", "subject", "rate", "opened", "sent", "openings", "clicks")
    inlines = [
        MailRecipientInline,
    ]
