"""
Django admin customization.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models


class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    # 어드민에서 유저 신규추가할 때 받을 필드들
    add_fieldsets = (
        (None, {
            # 'classes': ('wide', ),
            'fields': (
                'email',
                'password1',
                'password2',      
                'name',    
                'is_active', 
                'is_staff', 
                'is_superuser',        
            )
        }),
    )


# 어드민 화면에서 관리할 모델들을 써넣음!
admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe)
admin.site.register(models.Tag)
admin.site.register(models.Ingredient)