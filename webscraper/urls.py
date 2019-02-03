from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.generic.base import TemplateView
from .views import PostListView, PostDetailView, PostCreateView, PostUpdateView,\
    PostDeleteView, UserPostListView, WebscraperView, FilesListView
from . import views

urlpatterns = [
    path('', PostListView.as_view(), name='webscraper-home'),
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('files/<str:username>/', FilesListView.as_view(), name='user-files'),
    path('webscraper/', login_required(WebscraperView.as_view()), name='webscraper'),
    path('about/', views.about, name='webscraper-about'),
    path('download/', TemplateView.as_view(template_name='webscraper/download_file.html')),
    path('how-to', views.how_to, name='how-to'),
]
