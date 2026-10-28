# Generated initial migration for api app
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="Doctor's full name", max_length=255)),
                ('specialty', models.CharField(help_text='Medical specialty (e.g. Cardiology, Neurology)', max_length=255)),
                ('contact_info', models.CharField(help_text="Doctor's contact information", max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Doctor',
                'verbose_name_plural': 'Doctors',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Full name of the patient', max_length=255)),
                ('age', models.PositiveIntegerField(help_text='Age of the patient')),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], help_text='Gender of the patient', max_length=10)),
                ('contact_info', models.CharField(help_text='Contact telephone number, email, or address', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(help_text='The authenticated user who registered this patient', on_delete=django.db.models.deletion.CASCADE, related_name='patients', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Patient',
                'verbose_name_plural': 'Patients',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PatientDoctorMapping',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_at', models.DateTimeField(auto_now_add=True, help_text='Timestamp when mapping was established')),
                ('doctor', models.ForeignKey(help_text='The assigned doctor', on_delete=django.db.models.deletion.CASCADE, related_name='patient_mappings', to='api.doctor')),
                ('patient', models.ForeignKey(help_text='The assigned patient', on_delete=django.db.models.deletion.CASCADE, related_name='doctor_mappings', to='api.patient')),
            ],
            options={
                'verbose_name': 'Patient-Doctor Mapping',
                'verbose_name_plural': 'Patient-Doctor Mappings',
                'ordering': ['-assigned_at'],
                'unique_together': {('patient', 'doctor')},
            },
        ),
    ]
