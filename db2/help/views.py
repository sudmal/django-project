from django.shortcuts import render
from .models import ArticlePages


def ArticlePage(request,article_id):
    Artile_Page = ArticlePages.obgects.get(id=article_id)
    print(Artile_Page)
    context= {}
    return render(request, 'help/ArticlePage.html', context)
