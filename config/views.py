from django.conf import settings
from django.http import FileResponse, Http404, JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def spa_index(request):
    """Serve the Vue app for client-side routes such as /login or /tickets/5.

    The JS/CSS files themselves are served by WhiteNoise; this only answers the
    page URLs that the Vue router handles in the browser.
    """
    index = settings.FRONTEND_DIST / "index.html"
    if not index.exists():
        raise Http404("Frontend is not built. Run `npm run build` in frontend/.")
    return FileResponse(index.open("rb"), content_type="text/html")


@require_GET
def health(request):
    return JsonResponse({"status": "ok"})
