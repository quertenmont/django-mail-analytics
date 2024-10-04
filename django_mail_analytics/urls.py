"""
This module define url patterns for this app
"""

from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r"^i$", views.pixel, name="mail_pixel"),
    re_path(r"^p$", views.proxy, name="mail_proxy"),
    re_path(r"^l$", views.MailListView.as_view(), name="mail_list"),
]
