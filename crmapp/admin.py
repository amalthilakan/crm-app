from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Customer, UserProfile


# ── Customer Admin ────────────────────────────────────────────────────────────

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email_display', 'phone', 'created_at')
    search_fields = ('name', 'email', 'phone')

    @admin.display(description='Email')
    def email_display(self, obj):
        return obj.email

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('phone',)

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)

    list_display = ('username', 'email_display', 'first_name', 'last_name', 'is_staff')

    @admin.display(description='Email')
    def email_display(self, obj):
        return obj.email

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
