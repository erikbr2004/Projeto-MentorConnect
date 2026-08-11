from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, AlunoProfile, MentorProfile

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Função', {'fields': ('role',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(AlunoProfile)
admin.site.register(MentorProfile)
