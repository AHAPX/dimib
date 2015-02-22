from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from dimib.models import Account


class UserAdmin(DjangoUserAdmin):
    ordering = ('email',)


admin.site.register(Account, UserAdmin)
admin.site.unregister(Group)
