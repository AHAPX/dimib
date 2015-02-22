from django.conf import settings
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth import authenticate, login, logout

from rest_framework import viewsets
from rest_framework.decorators import api_view, detail_route
from rest_framework.response import Response

from dimib.models import Account, Post, Comment, Tag
from dimib.serializers import AccountSerializer, PostSerializer, CommentSerializer
from dimib.forms import RegistrationForm, PostForm, CommentForm
from dimib.pgplib import generateKey, verify


class BaseApiViewSet(viewsets.ViewSet):

    def message (self, msg):
        return Response(msg)

    def success (self):
        return self.message({'success': True})

    def error (self, err):
        return self.message({'errors': err})

    def error_form (self, form):
        return Response(form.errors.as_json())


class ApiAuth (BaseApiViewSet):

    def registrate (self, request):
        form = RegistrationForm(request.DATA)
        if form.is_valid():
            private_key = generateKey(form.cleaned_data['username'])
            if private_key:
                account = form.save(commit = False)
                account.set_password(account.username)
                account.save()
                return self.message({'key': private_key})
            return self.error('key not created')
        return self.error_form(form)

    def get_user (self, request):
        if request.user.is_authenticated():
            return self.message(AccountSerializer(request.user).data)
        else:
            return self.message({'username': 'anonymous'})

    def login (self, request):
        data = request.DATA['data']
        signature = request.DATA['signature']
        if verify(data, data, signature):
            user = authenticate(username = data, password = data)
            if user:
                login(request, user)
                return self.success()
        return self.error('wrong signature')

    def logout (self, request):
        logout(request)
        return self.success()


class ApiPost (BaseApiViewSet):

    def get_posts (self, request):
        return self.message({'posts': PostSerializer(Post.objects.all(), many=True).data})

    def add_post (self, request):
        if not request.DATA.get('data'):
            return self.error('no data')
        form = PostForm(request.DATA['data'])
        if form.is_valid():
            record = form.save(commit = False)
            if request.user.is_authenticated():
                record.account = request.user
                if request.DATA.get('signature') and verify(request.user.username, record.message, request.DATA['signature']):
                    record.verified = True
            record.save()
            if request.DATA['data'].get('tags'):
                for tag_name in request.DATA['data']['tags']:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    record.tags.add(tag)
                record.save()
            return self.success()
        return self.error_form(form)

    def get_post (self, request, post_id):
        try:
            record = Post.objects.get(pk = post_id)
        except Post.DoesNotExist:
            return self.error('Post not found')
        else:
            return self.message(PostSerializer(record).data)

    def add_comment(self, request, post_id):
        if not request.DATA.get('data'):
            return self.error('no data')
        try:
            post = Post.objects.get(pk = post_id)
        except Post.DoesNotExist:
            return self.error('Post not found')
        form = CommentForm(request.DATA['data'])
        if form.is_valid():
            record = form.save(commit = False)
            record.post = post
            if request.DATA.get('comment_id'):
                try:
                    comment = Comment.objects.get(pk = request.DATA['comment_id'])
                except Comment.DoesNotExist:
                    pass
                else:
                    if comment.post == post:
                        record.comment = comment
            if request.user.is_authenticated():
                record.account = request.user
                if request.DATA.get('signature') and verify(request.user.username, record.message, request.DATA['signature']):
                    record.verified = True
            record.save()
            return self.success()
        return self.error_form(form)

    def get_comments (self, request, post_id):
        try:
            record = Post.objects.get(pk = post_id)
        except Post.DoesNotExist:
            return self.error('Post not found')
        else:
            return self.message({'comments': CommentSerializer(record.comments.all(), many=True).data})




