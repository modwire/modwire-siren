from django.http import JsonResponse


class DjangoArticleView:
    def __call__(self, request, article_id):
        return JsonResponse({"article_id": article_id, "title": "Installed"})


django_article_view = DjangoArticleView()
