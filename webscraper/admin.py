from django.contrib import admin
from .models import Killboard, Post
from django.utils.safestring import mark_safe


class KillboardAdmin(admin.ModelAdmin):
    def file_link(self, obj):
        return mark_safe('<a href="%s">Download</a>' % obj.excel_file)

    file_link.allow_tags = True
    list_display = ('date', 'user', 'fight_name', 'file_link')
    list_filter = ('date', 'user')


admin.site.register(Post)
admin.site.register(Killboard, KillboardAdmin)
