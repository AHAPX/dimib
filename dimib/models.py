from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager


class Server (models.Model):
    name = models.CharField(max_length=30)
    url = models.URLField()

    def __str__ (self):
        return self.name

    class Meta:
        db_table = 'servers'


class Account (AbstractUser):
    server = models.ForeignKey(Server, related_name='accounts', null=True)

    def __str__ (self):
        return self.username

    class Meta:
        db_table = 'accounts'


class Tag (models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__ (self):
        return self.name

    class Meta:
        db_table = 'tags'


class Post (models.Model):
    account = models.ForeignKey(Account, null=True)
    tags = models.ManyToManyField('Tag', blank=True)
    message = models.CharField(max_length=settings.POST_LENGTH)
    ts_created = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'posts'


class Comment (models.Model):
    account = models.ForeignKey(Account, null=True)
    post = models.ForeignKey(Post, related_name='comments')
    comment = models.ForeignKey('Comment', related_name='comments', null=True)
    message = models.CharField(max_length=settings.COMMENT_LENGTH)
    ts_created = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'comments'
    
