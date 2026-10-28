from django.contrib import admin
from .models import Patient, Doctor, PatientDoctorMapping


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'age', 'gender', 'contact_info', 'created_by', 'created_at')
    search_fields = ('name', 'contact_info', 'created_by__username', 'created_by__email')
    list_filter = ('gender', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'specialty', 'contact_info', 'created_at')
    search_fields = ('name', 'specialty', 'contact_info')
    list_filter = ('specialty', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(PatientDoctorMapping)
class PatientDoctorMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'assigned_at')
    search_fields = ('patient__name', 'doctor__name', 'doctor__specialty')
    list_filter = ('assigned_at',)
    readonly_fields = ('assigned_at',)
