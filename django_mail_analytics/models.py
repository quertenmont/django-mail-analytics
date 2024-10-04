from django.db import models


class Mail(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    key = models.CharField(null=False, max_length=128, db_index=True)
    date = models.DateField(null=False, editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    sender = models.CharField(null=True, max_length=2048)  # noqa: DJ001
    subject = models.CharField(null=True, max_length=2048)  # noqa: DJ001
    body = models.TextField(null=True, blank=True)  # noqa: DJ001

    def __str__(self):
        return f"Mail-{self.pk}"


class MailRecipient(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    mail = models.ForeignKey(
        Mail, on_delete=models.CASCADE, null=False, related_name="recipients"
    )
    recipient = models.CharField(null=False, max_length=2048)

    def __str__(self):
        return f"MailRecipient-{self.pk}"

    @property
    def email(self):
        return self.recipient

    @property
    def created(self):
        return self.mail.created

    @property
    def mail_key(self):
        return self.mail.key


class MailRecipientAction(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    recipient = models.ForeignKey(
        MailRecipient, on_delete=models.CASCADE, null=False, related_name="actions"
    )
    created = models.DateTimeField(auto_now_add=True, editable=False)
    action = models.CharField(null=False, max_length=2048)

    def __str__(self):
        return f"MailRecipientAction-{self.pk}"

    @property
    def recipient_email(self):
        return self.recipient.recipient

    @property
    def recipient_mail_key(self):
        return self.recipient.mail.key
