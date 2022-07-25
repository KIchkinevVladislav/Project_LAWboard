
from django.forms import ModelForm, Textarea

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        required = {
            'group': False,
        }
        labels = {
            'group': 'Тематика',
            'text': 'Текст записи',
            'image': 'Изображение'
        }
        help_texts = {
            'group': 'Укажите тематику сообщения.'
        }

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text', )
        widgets = {
            'text': Textarea
        }
        labels = {
            'text': 'Комментарий'
        }
