# Generated by Django 2.1.5 on 2019-01-28 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webscraper', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='KillboardUrl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=200)),
                ('killboard_id', models.IntegerField()),
            ],
        ),
        migrations.DeleteModel(
            name='KillboardUrls',
        ),
    ]
