from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class CustomUserAdmin(UserAdmin):
	list_display = ('username', 'email', 'numero_control', 'es_admin_creditos', 'es_alumno', 'is_staff')
	list_filter = ('es_admin_creditos', 'es_alumno', 'is_staff')
	fieldsets = UserAdmin.fieldsets + (
		('Información adicional', {'fields': ('numero_control', 'es_admin_creditos', 'es_alumno')}),
	)
	add_fieldsets = UserAdmin.add_fieldsets + (
		('Información adicional', {'fields': ('numero_control', 'es_admin_creditos', 'es_alumno')}),
	)
