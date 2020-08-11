from django import forms
from .models import Topic, Post


class NewTopicForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 5, 'placeholder': 'What is on your mind?'}
        ),
        max_length=4000,
        help_text='The max length of the text is 4000.'
    )
    image = forms.ImageField(required=False)

    class Meta:
        model = Topic
<<<<<<< HEAD
        fields = ['subject', 'message', 'image' ]
=======
        fields = ['subject', 'message', ]
>>>>>>> 946d3bd... Now can edit and remove images everywhere

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['message', 'image', ]