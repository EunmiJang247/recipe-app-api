"""
장고 어드민 커스텀하기 
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models

class UserAdmin(BaseUserAdmin):
    """ 어드민 페이지를 정의 """
    ordering = ['id'] #순서는 id로 
    list_display = ['email', 'name'] #email, name을 리스트로 보여줄것이다
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Permissons'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates', {'fields': ('last_login')}))
    )
    readonly_fields = ['last_login']

admin.site.register(models.User) #유저 모델을 등록함