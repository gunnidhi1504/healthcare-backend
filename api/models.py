from django.db import models
from django.contrib.auth.models import User


class Patient(models.Model):
    """
    Model representing a patient in the healthcare system.
    Created and managed by authenticated users.
    """
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )

    name = models.CharField(max_length=255, help_text="Full name of the patient")
    age = models.PositiveIntegerField(help_text="Age of the patient")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, help_text="Gender of the patient")
    contact_info = models.CharField(max_length=255, help_text="Contact telephone number, email, or address")
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='patients',
        help_text="The authenticated user who registered this patient"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'

    def __str__(self):
        return f"{self.name} (Age: {self.age}, Gender: {self.gender})"


class Doctor(models.Model):
    """
    Model representing a medical doctor.
    """
    name = models.CharField(max_length=255, help_text="Full name of the doctor")
    specialty = models.CharField(max_length=255, help_text="Medical specialty (e.g. Cardiology, Neurology)")
    contact_info = models.CharField(max_length=255, help_text="Doctor's contact information")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Doctor'
        verbose_name_plural = 'Doctors'

    def __str__(self):
        return f"Dr. {self.name} - {self.specialty}"


class PatientDoctorMapping(models.Model):
    """
    Model managing assignments between patients and doctors.
    """
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='doctor_mappings',
        help_text="The assigned patient"
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='patient_mappings',
        help_text="The assigned doctor"
    )
    assigned_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when mapping was established")

    class Meta:
        unique_together = ('patient', 'doctor')
        ordering = ['-assigned_at']
        verbose_name = 'Patient-Doctor Mapping'
        verbose_name_plural = 'Patient-Doctor Mappings'

    def __str__(self):
        return f"Mapping: {self.patient.name} -> Dr. {self.doctor.name} ({self.doctor.specialty})"
