from django.contrib import admin
from .models import Killboard, Post

admin.site.register(Post)
admin.site.register(Killboard)
