# Generated by Django 4.0 on 2022-07-16 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0007_follow'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('created',), 'verbose_name': 'Комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
        migrations.AlterModelOptions(
            name='group',
            options={'ordering': ('title',), 'verbose_name': 'Тематика', 'verbose_name_plural': 'Тематики'},
        ),
        migrations.RenameField(
            model_name='comment',
            old_name='create',
            new_name='created',
        ),
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(help_text='Опишите тематику', verbose_name='Описание тематики'),
        ),
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(help_text='Укажите адрес для страницы. Используйте только латиницу, цифры, дефисы и знаки подчёркивания', unique=True, verbose_name='Уникальный адрес'),
        ),
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(max_length=200, verbose_name='Тематика сообщений'),
        ),
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, help_text='Загрузите изображение', null=True, upload_to='posts/', verbose_name='Изображение'),
        ),
    ]
