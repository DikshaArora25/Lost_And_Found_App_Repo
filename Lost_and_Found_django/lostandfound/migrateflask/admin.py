from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import AppUser


class AppUserAdmin(UserAdmin):
    model = AppUser
    list_display = ('email', 'name', 'is_staff', 'is_superuser', 'gender', 'address', 'phone', 'dob')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'phone', 'address', 'gender', 'dob')}),
        ('Permissions', {'fields': ('is_active', 'is_staff',
                                    'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'phone', 'address', 'gender', 'dob', 'password1', 'password2'),
        }),
    )


admin.site.register(AppUser, AppUserAdmin)

from django.contrib import admin
from .models import Item

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'date', 'location', 'status')  # Columns in admin panel
    search_fields = ('name', 'category', 'location')  # Enable search
    list_filter = ('category', 'date', 'status')  # Filtering options

    

from django.contrib import admin
from .models import ContactforClaim

@admin.register(ContactforClaim)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'product', 'date')

