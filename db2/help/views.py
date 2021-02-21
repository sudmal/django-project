from django.shortcuts import render
from .models import ArticlePage

def index(request):
    context= {}
    return render(request, 'help/index.html', context)


def ArticlePageView(request,article_id):
    Artile_Page = ArticlePage.objects.get(id=article_id)
    page_title=Artile_Page.Title
    page_text=Artile_Page.Text
    context= {
        'page_text':page_text,
        'page_title': page_title,
    }
    return render(request, 'help/ArticlePage.html', context)
