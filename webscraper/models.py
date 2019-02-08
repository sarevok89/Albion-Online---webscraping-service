from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User


class Killboard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fight_name = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now)
    excel_file = models.FileField(upload_to='compensations')

    def __str__(self):
        return self.fight_name


class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={'pk': self.pk})
