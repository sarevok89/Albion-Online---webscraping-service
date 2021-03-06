# Generated by Django 2.1.5 on 2019-02-01 10:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('webscraper', '0006_auto_20190130_1505'),
    ]

    operations = [
        migrations.CreateModel(
            name='Killboard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fight_name', models.CharField(max_length=100)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('excel_file', models.FileField(upload_to='webscraper/compensations')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='killboardexcelfiles',
            name='user',
        ),
        migrations.DeleteModel(
            name='KillboardExcelFiles',
        ),
    ]
