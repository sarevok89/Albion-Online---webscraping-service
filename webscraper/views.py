from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.core.files import File
from .forms import WebscraperForm
from .models import Killboard, Post
from webscraper.static.webscraper.killboard_app import create_table, create_kill_id_list, generate_excel
from albion_compensations.settings import BASE_DIR, MEDIA_ROOT, MEDIA_S3_ROOT, MEDIA_URL
# from albion_compensations.aws.conf import *
import boto3
import os


class WebscraperView(View):
    template_name = 'webscraper/webscraper.html'
    form_class = WebscraperForm

    def get(self, request, *args, **kwargs):
        form = WebscraperForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = WebscraperForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['urls']
            fight_name = form.cleaned_data['fight_name']
            kill_id_list = create_kill_id_list(text)
            dict_list = create_table(kill_id_list)
            file_name = generate_excel(dict_list, fight_name)

            obj = Killboard()
            obj.fight_name = fight_name
            obj.user = self.request.user

            temp_file = os.path.join(MEDIA_ROOT, 'compensations', file_name)

            s3 = boto3.resource('s3', aws_access_key_id='AKIAJZ7G7LLNHVOEGTKA',
                                aws_secret_access_key='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')
            s3.meta.client.upload_file(temp_file, 'albion-compensations', 'media/compensations/test.xlsx')

            obj.excel_file.name = MEDIA_URL + 'compensations/' + file_name

            obj.save()

            context = {
                'file_url': obj.excel_file.name,
                'file_name': file_name
            }

            return render(request, 'webscraper/download_file.html', context)


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
        user = get_object_or_404(User, username=self.kwargs.get('username'))
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
        return Killboard.objects.filter(user=self.request.user).order_by('-date')


def about(request):
    return render(request, 'webscraper/about.html')


def how_to(request):
    return render(request, 'webscraper/how_to.html')
