# Create your views here.


from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count, F, Q
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import ListView

from .mail import mail_settings, register_action
from .models import Mail


#def generate_pixel_bytes(request):
#    # generate the pixel bytes from scratch
#    import io
#
#    from PIL import Image
#
#    pixel = Image.new("RGBA", (1, 1), (255, 255, 255, 0))
#    content = io.BytesIO()
#    pixel.save(content, "PNG")
#    pixel_bytes = content.getvalue()
#    return pixel_bytes


async def proxy(request):
    q = request.GET.get("q", None)
    url = request.GET.get("u", None)
    if not url:
        scheme = mail_settings()["SCHEME"]
        domain = mail_settings()["DOMAIN"]
        HttpResponseRedirect(f"{scheme}://{domain}/")

    await register_action(q, url)
    return HttpResponseRedirect(url)


async def pixel(request):
    q = request.GET.get("q", None)

    # hardcode pixel value to save time, it never changes, use generate_pixel_bytes if you need to update
    pixel_bytes = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00"
        b"\x00\x00\rIDATx\x9cc\xf8\xff\xff?\x03\x00\x08\xfc\x02\xfe\xa7\x9a\xa0\xa0\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    await register_action(q)
    return HttpResponse(content=pixel_bytes, content_type="image/png")


class MailListView(PermissionRequiredMixin, ListView):
    permission_required = ["is_staff"]

    paginate_by = 25
    model = Mail

    def get_queryset(self):
        opening = Q(recipients__actions__action="")
        hasAction = Q(recipients__actions__isnull=False)
        qs = Mail.objects.all()
        qs = qs.annotate(opened=Count("recipients", filter=hasAction & opening, distinct=True))
        qs = qs.annotate(sent=Count("recipients", distinct=True))
        qs = qs.annotate(openings=Count("recipients__actions", filter=opening))
        qs = qs.annotate(clicks=Count("recipients__actions", filter=~opening))
        qs = qs.annotate(rate=(F("opened") / F("sent")) * 100)
        qs = qs.order_by("-created")
        return qs
