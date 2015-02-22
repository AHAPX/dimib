from rest_framework import serializers

from dimib.models import Account, Post, Comment, Tag


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('username',)


class PostSerializer(serializers.ModelSerializer):
    account = serializers.StringRelatedField(read_only=True)
    tags = serializers.StringRelatedField(many=True)

    class Meta:
        model = Post
        fields = ('pk', 'account', 'message', 'tags', 'ts_created', 'verified',)


class CommentSerializer(serializers.ModelSerializer):
    account = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ('pk', 'account', 'message', 'post', 'comment', 'ts_created', 'verified',)

