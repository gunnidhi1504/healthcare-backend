from django.shortcuts import get_object_or_404
from rest_framework import status, permissions, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Patient, Doctor, PatientDoctorMapping
from .serializers import (
    UserRegistrationSerializer,
    PatientSerializer,
    DoctorSerializer,
    PatientDoctorMappingSerializer,
)


# ============================================================================
# 1. Authentication APIs
# ============================================================================

class RegisterView(APIView):
    """
    POST /api/auth/register/
    Registers a new user with name, email, and password using UserRegistrationSerializer.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User registered successfully.",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "name": f"{user.first_name} {user.last_name}".strip(),
                    }
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================================================
# 2. Doctor Management API (ModelViewSet)
# ============================================================================

class DoctorViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for Doctor management mapped to /api/doctors/.
    Requires authentication (IsAuthenticated) for all endpoints.

    Supported Operations:
      - GET    /api/doctors/        -> List all doctors
      - GET    /api/doctors/<id>/   -> Retrieve specific doctor details
      - POST   /api/doctors/        -> Add a new doctor
      - PUT    /api/doctors/<id>/   -> Update doctor details
      - PATCH  /api/doctors/<id>/   -> Partially update doctor details
      - DELETE /api/doctors/<id>/   -> Delete a doctor record
    """
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]


# ============================================================================
# 3. Patient Management API (ModelViewSet)
# ============================================================================

class PatientViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for Patient management mapped to /api/patients/.
    Requires authentication (IsAuthenticated) for all endpoints.

    Overrides get_queryset so that authenticated users can only retrieve,
    update, or delete patients they specifically created.

    Supported Operations:
      - GET    /api/patients/        -> List all patients created by the authenticated user
      - GET    /api/patients/<id>/   -> Retrieve specific patient (only if created by user)
      - POST   /api/patients/        -> Create a new patient (sets created_by to request.user)
      - PUT    /api/patients/<id>/   -> Update patient details (only if created by user)
      - PATCH  /api/patients/<id>/   -> Partially update patient (only if created by user)
      - DELETE /api/patients/<id>/   -> Delete patient record (only if created by user)
    """
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Users can only retrieve, update, or delete patients they specifically created.
        """
        user = self.request.user
        if user.is_authenticated:
            return Patient.objects.filter(created_by=user)
        return Patient.objects.none()

    def perform_create(self, serializer):
        """
        Automatically set created_by to the current authenticated user on creation.
        """
        serializer.save(created_by=self.request.user)


# ============================================================================
# 4. Patient-Doctor Mapping API (ModelViewSet)
# ============================================================================

class PatientDoctorMappingViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for Patient-Doctor Mappings mapped to /api/mappings/.
    Requires authentication (IsAuthenticated) for all endpoints.

    Supported Operations:
      - GET    /api/mappings/              -> List all patient-doctor mappings
      - POST   /api/mappings/              -> Assign a doctor to a patient
      - DELETE /api/mappings/<id>/         -> Remove a doctor from a patient (delete mapping)
      - GET    /api/mappings/<patient_id>/ -> Custom action to retrieve all doctors assigned
                                              to a specific patient
    """
    queryset = PatientDoctorMapping.objects.all().select_related('patient', 'doctor')
    serializer_class = PatientDoctorMappingSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get', 'delete'], url_path=r'(?P<patient_id>\d+)')
    def doctors_by_patient(self, request, patient_id=None):
        """
        GET  /api/mappings/<patient_id>/ -> Retrieve all doctors assigned to a specific patient.
        DELETE /api/mappings/<id>/         -> Remove a doctor from a patient (delete mapping by mapping ID).
        """
        if request.method.lower() == 'delete':
            mapping = get_object_or_404(PatientDoctorMapping, pk=patient_id)
            patient_name = mapping.patient.name
            doctor_name = mapping.doctor.name
            mapping.delete()
            return Response(
                {
                    "message": f"Successfully unassigned Dr. {doctor_name} from patient {patient_name}."
                },
                status=status.HTTP_200_OK
            )

        # GET: Retrieve all doctors assigned to a specific patient
        patient = get_object_or_404(Patient, pk=patient_id)
        mappings = self.get_queryset().filter(patient=patient).select_related('doctor')
        doctors = [mapping.doctor for mapping in mappings]
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path=r'patient/(?P<patient_id>\d+)')
    def doctors_by_patient_alias(self, request, patient_id=None):
        """
        GET /api/mappings/patient/<patient_id>/ (Convenience route)
        """
        return self.doctors_by_patient(request, patient_id=patient_id)

    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/mappings/<id>/
        Removes a doctor from a patient using the mapping ID.
        """
        instance = self.get_object()
        patient_name = instance.patient.name
        doctor_name = instance.doctor.name
        self.perform_destroy(instance)
        return Response(
            {
                "message": f"Successfully unassigned Dr. {doctor_name} from patient {patient_name}."
            },
            status=status.HTTP_200_OK
        )
