from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey

User = get_user_model()

class Group(models.Model):
    title = models.CharField(
        verbose_name='Тематика сообщений',
        max_length=200
    )
    description = models.TextField(
        verbose_name='Описание тематики',
        help_text='Опишите тематику'
    )
    slug = models.SlugField(
        verbose_name='Уникальный адрес',
        unique=True,
        help_text=('Укажите адрес для страницы. Используйте '
                   'только латиницу, цифры, дефисы и знаки '
                   'подчёркивания')
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Тематики'
        verbose_name = 'Тематика'
        ordering = ('title',)



class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Введите текст'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='posts',
        help_text='Укажите группу')
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='posts/', 
        blank=True,
        null=True,
        help_text='Загрузите изображение'
    )
    
    
    class Meta:
        verbose_name_plural = 'Записи'
        verbose_name = 'Запись'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    text = models.TextField()
    created = models.DateTimeField(
        verbose_name='Дата комментария',
        auto_now_add=True
    ) 
        
    def __str__(self):
        return self.text

    class Meta:
        verbose_name_plural = 'Комментарии'
        verbose_name = 'Комментарий'
        ordering = ('created',)

class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='following')
    
    class Meta:
        unique_together = ('user', 'author')

