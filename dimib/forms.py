from django import forms

from dimib.models import Account, Post, Comment


class RegistrationForm (forms.ModelForm):
    class Meta:
        model = Account
        fields = ['username',]


class PostForm (forms.ModelForm):
    class Meta:
        model = Post
        fields = ['message',]


class CommentForm (forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['message',]
