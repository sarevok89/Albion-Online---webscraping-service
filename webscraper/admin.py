from django.contrib import admin
from .models import Killboard, Post


class KillboardAdmin(admin.ModelAdmin):
    list_display = ('date', 'user', 'fight_name', 'excel_file')


admin.site.register(Post)
admin.site.register(Killboard, KillboardAdmin)
