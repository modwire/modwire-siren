from django.http import JsonResponse


class DjangoRootView:
    def __call__(self, request):
        return JsonResponse({"status": "ready"})


django_root_view = DjangoRootView()
