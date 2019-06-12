import json

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404
from django.views.generic import View, ListView, DetailView, CreateView, \
    UpdateView, DeleteView

from webscraper.forms import WebscraperForm
from webscraper.models import Killboard, Post
from albion_compensations.wsgi import publisher


class WebscraperView(View):
    template_name = 'webscraper/webscraper.html'
    form_class = WebscraperForm

    def get(self, request, *args, **kwargs):
        form = WebscraperForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        publisher.connect('webscraper')
        form = WebscraperForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['urls']
            fight_name = form.cleaned_data['fight_name']

            body = json.dumps({'text': text,
                               'fight_name': fight_name,
                               'user': self.request.user.username})

            publisher.publish('webscraper', body)

            return render(request, 'webscraper/download_file.html')


def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'webscraper/home.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'webscraper/home.html'    # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = 'webscraper/user_posts.html'    # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(
            self.request.user, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class FilesListView(LoginRequiredMixin, ListView):
    model = Killboard
    template_name = 'webscraper/user_files.html'
    context_object_name = 'files'
    ordering = ['-date']
    paginate_by = 10

    def get_queryset(self):
        return Killboard.objects.filter(
            user=self.request.user).order_by('-date')


def about(request):
    return render(request, 'webscraper/about.html')


def how_to(request):
    return render(request, 'webscraper/how_to.html')
