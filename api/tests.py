from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Patient, Doctor, PatientDoctorMapping


class ModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='doctorwho',
            email='who@tardis.org',
            password='Password123!'
        )
        self.patient = Patient.objects.create(
            name='Sarah Jane',
            age=32,
            gender='Female',
            contact_info='sarah@journal.co.uk',
            created_by=self.user
        )
        self.doctor = Doctor.objects.create(
            name='The Doctor',
            specialty='Time Lord Medicine',
            contact_info='tardis@box.space'
        )
        self.mapping = PatientDoctorMapping.objects.create(
            patient=self.patient,
            doctor=self.doctor
        )

    def test_patient_str(self):
        expected_str = f"{self.patient.name} (Age: {self.patient.age}, Gender: {self.patient.gender})"
        self.assertEqual(str(self.patient), expected_str)

    def test_doctor_str(self):
        expected_str = f"Dr. {self.doctor.name} - {self.doctor.specialty}"
        self.assertEqual(str(self.doctor), expected_str)

    def test_mapping_str(self):
        expected_str = f"Mapping: {self.patient.name} -> Dr. {self.doctor.name} ({self.doctor.specialty})"
        self.assertEqual(str(self.mapping), expected_str)


class APITests(APITestCase):
    def setUp(self):
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.patients_url = '/api/patients/'
        self.doctors_url = '/api/doctors/'
        self.mappings_url = '/api/mappings/'

        # Create two distinct users
        self.user1 = User.objects.create_user(username='alice', email='alice@test.com', password='Password123!')
        self.user2 = User.objects.create_user(username='bob', email='bob@test.com', password='Password123!')

    def test_patient_and_mapping_viewsets(self):
        # 1. Login user1
        res_login = self.client.post(self.login_url, {"email": "alice@test.com", "password": "Password123!"}, format='json')
        self.assertEqual(res_login.status_code, status.HTTP_200_OK)
        token1 = res_login.data['access']

        # 2. Login user2
        res_login2 = self.client.post(self.login_url, {"email": "bob@test.com", "password": "Password123!"}, format='json')
        self.assertEqual(res_login2.status_code, status.HTTP_200_OK)
        token2 = res_login2.data['access']

        # 3. PatientViewSet requires authentication
        self.client.credentials()  # clear credentials
        res_unauth = self.client.get(self.patients_url)
        self.assertEqual(res_unauth.status_code, status.HTTP_401_UNAUTHORIZED)

        # 4. User1 creates Patient A
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token1}')
        res_patient1 = self.client.post(self.patients_url, {
            "name": "Patient One",
            "age": 45,
            "gender": "Male",
            "contact_info": "p1@test.com"
        }, format='json')
        self.assertEqual(res_patient1.status_code, status.HTTP_201_CREATED)
        patient1_id = res_patient1.data['id']
        self.assertEqual(res_patient1.data['created_by'], 'alice')

        # 5. User2 creates Patient B
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token2}')
        res_patient2 = self.client.post(self.patients_url, {
            "name": "Patient Two",
            "age": 28,
            "gender": "Female",
            "contact_info": "p2@test.com"
        }, format='json')
        self.assertEqual(res_patient2.status_code, status.HTTP_201_CREATED)
        patient2_id = res_patient2.data['id']

        # 6. Verify isolation: User2 cannot see Patient A (created by User1)
        res_list2 = self.client.get(self.patients_url)
        self.assertEqual(res_list2.status_code, status.HTTP_200_OK)
        ids = [p['id'] for p in res_list2.data]
        self.assertIn(patient2_id, ids)
        self.assertNotIn(patient1_id, ids)

        # 7. User2 cannot retrieve Patient A
        res_get_other = self.client.get(f'{self.patients_url}{patient1_id}/')
        self.assertEqual(res_get_other.status_code, status.HTTP_404_NOT_FOUND)

        # 8. User1 can retrieve, update, and delete Patient A
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token1}')
        res_update = self.client.put(f'{self.patients_url}{patient1_id}/', {
            "name": "Patient One Updated",
            "age": 46,
            "gender": "Male",
            "contact_info": "p1_updated@test.com"
        }, format='json')
        self.assertEqual(res_update.status_code, status.HTTP_200_OK)
        self.assertEqual(res_update.data['name'], "Patient One Updated")

        # 9. Create a Doctor
        res_doc = self.client.post(self.doctors_url, {
            "name": "Dr. Watson",
            "specialty": "General Medicine",
            "contact_info": "watson@bakerst.co.uk"
        }, format='json')
        self.assertEqual(res_doc.status_code, status.HTTP_201_CREATED)
        doctor_id = res_doc.data['id']

        # 10. Assign Doctor to Patient A via PatientDoctorMappingViewSet (POST /api/mappings/)
        res_map = self.client.post(self.mappings_url, {
            "patient_id": patient1_id,
            "doctor_id": doctor_id
        }, format='json')
        self.assertEqual(res_map.status_code, status.HTTP_201_CREATED)
        mapping_id = res_map.data['id']

        # 11. Custom @action: GET /api/mappings/<patient_id>/ retrieves assigned doctors
        res_patient_doctors = self.client.get(f'{self.mappings_url}{patient1_id}/')
        self.assertEqual(res_patient_doctors.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_patient_doctors.data), 1)
        self.assertEqual(res_patient_doctors.data[0]['name'], "Dr. Watson")

        # 12. Delete mapping: DELETE /api/mappings/<id>/
        res_del_map = self.client.delete(f'{self.mappings_url}{mapping_id}/')
        self.assertEqual(res_del_map.status_code, status.HTTP_200_OK)

        # 13. Delete Patient A: DELETE /api/patients/<id>/
        res_del_patient = self.client.delete(f'{self.patients_url}{patient1_id}/')
        self.assertEqual(res_del_patient.status_code, status.HTTP_204_NO_CONTENT)

        # 14. Update Doctor: PUT /api/doctors/<id>/
        res_put_doc = self.client.put(f'{self.doctors_url}{doctor_id}/', {
            "name": "Dr. John H. Watson",
            "specialty": "Forensic Medicine",
            "contact_info": "john.watson@bakerst.co.uk"
        }, format='json')
        self.assertEqual(res_put_doc.status_code, status.HTTP_200_OK)
        self.assertEqual(res_put_doc.data['name'], "Dr. John H. Watson")

        # 15. Delete Doctor: DELETE /api/doctors/<id>/
        res_del_doc = self.client.delete(f'{self.doctors_url}{doctor_id}/')
        self.assertEqual(res_del_doc.status_code, status.HTTP_204_NO_CONTENT)
