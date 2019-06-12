from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic.base import TemplateView

from webscraper import views

urlpatterns = [
    path('', views.PostListView.as_view(), name='webscraper-home'),
    path('user/<str:username>',
         views.UserPostListView.as_view(), name='user-posts'),
    path('post/<int:pk>/',
         views.PostDetailView.as_view(), name='post-detail'),
    path('post/new/',
         views.PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/',
         views.PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/',
         views.PostDeleteView.as_view(), name='post-delete'),
    path('files/<str:username>/',
         views.FilesListView.as_view(), name='user-files'),
    path('webscraper/',
         login_required(views.WebscraperView.as_view()), name='webscraper'),
    path('about/',
         views.about, name='webscraper-about'),
    path('download/',
         TemplateView.as_view(template_name='webscraper/download_file.html')),
    path('how-to',
         views.how_to, name='how-to'),
]
