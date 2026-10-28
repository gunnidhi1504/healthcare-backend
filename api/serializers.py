from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Patient, Doctor, PatientDoctorMapping


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom TokenObtainPairSerializer supporting login with either username or email.
    Accepts both 'username' and 'email' fields in the POST request body.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field].required = False
        self.fields['email'] = serializers.EmailField(required=False)

    def validate(self, attrs):
        email = attrs.get('email')
        username = attrs.get('username')
        if not username and email:
            attrs['username'] = email
        return super().validate(attrs)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Creates a standard Django User with name, email, and password,
    securely hashing the password using Django's authentication system.
    """
    name = serializers.CharField(write_only=True, required=True, max_length=150)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password']
        read_only_fields = ['id']

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email address already exists.")
        return value

    def create(self, validated_data):
        name = validated_data.pop('name', '').strip()
        email = validated_data.get('email', '').strip()
        password = validated_data.pop('password')

        # Parse first and last names
        name_parts = name.split(None, 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Generate a unique username based on the email prefix
        base_username = email.split('@')[0] if email else 'user'
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        # create_user securely hashes the password using Django's PBKDF2 password hasher
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user authentication / login.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )


class DoctorSerializer(serializers.ModelSerializer):
    """
    Serializer for Doctor model CRUD operations.
    """
    class Meta:
        model = Doctor
        fields = [
            'id',
            'name',
            'specialty',
            'contact_info',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer for Patient model CRUD operations.
    Automatically sets the 'created_by' field to the currently authenticated user
    and marks it read-only in responses.
    """
    created_by = serializers.ReadOnlyField(source='created_by.username')
    created_by_id = serializers.ReadOnlyField(source='created_by.id')

    class Meta:
        model = Patient
        fields = [
            'id',
            'name',
            'age',
            'gender',
            'contact_info',
            'created_by',
            'created_by_id',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_by_id', 'created_at', 'updated_at']

    def validate_age(self, value):
        if value < 0 or value > 150:
            raise serializers.ValidationError("Age must be between 0 and 150.")
        return value

    def create(self, validated_data):
        # Automatically assign current authenticated user from request context if not already set
        request = self.context.get('request', None)
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class PatientDoctorMappingSerializer(serializers.ModelSerializer):
    """
    Serializer for PatientDoctorMapping model.
    Returns the mapping ID along with full nested details of the assigned doctor and patient.
    Accepts patient_id (or patient) and doctor_id (or doctor) on creation.
    """
    patient_id = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        source='patient',
        write_only=True,
        required=False,
        help_text="ID of the patient"
    )
    doctor_id = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(),
        source='doctor',
        write_only=True,
        required=False,
        help_text="ID of the doctor"
    )
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = [
            'id',
            'patient_id',
            'doctor_id',
            'patient',
            'doctor',
            'assigned_at',
        ]
        read_only_fields = ['id', 'patient', 'doctor', 'assigned_at']

    def to_internal_value(self, data):
        # Support passing either 'patient'/'patient_id' and 'doctor'/'doctor_id'
        data_copy = data.copy() if hasattr(data, 'copy') else dict(data)
        if 'patient' in data_copy and 'patient_id' not in data_copy and not isinstance(data_copy['patient'], dict):
            data_copy['patient_id'] = data_copy['patient']
        if 'doctor' in data_copy and 'doctor_id' not in data_copy and not isinstance(data_copy['doctor'], dict):
            data_copy['doctor_id'] = data_copy['doctor']
        return super().to_internal_value(data_copy)

    def validate(self, attrs):
        patient = attrs.get('patient')
        doctor = attrs.get('doctor')

        if not patient or not doctor:
            raise serializers.ValidationError("Both patient and doctor are required.")

        if PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
            raise serializers.ValidationError(
                {"detail": f"Patient '{patient.name}' is already assigned to Dr. '{doctor.name}'."}
            )
        return attrs
