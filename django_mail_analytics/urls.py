"""
This module define url patterns for this app
"""

from django.urls import path

from . import views

urlpatterns = [
    path("i", views.pixel, name="mail_pixel"),
    path("p", views.proxy, name="mail_proxy"),
    path("l", views.MailListView.as_view(), name="mail_list"),
]
