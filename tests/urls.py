from django.contrib import admin
from django.urls import path
from django.urls import include, re_path


urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
    path("m/", include("django_mail_analytics.urls")),
]
