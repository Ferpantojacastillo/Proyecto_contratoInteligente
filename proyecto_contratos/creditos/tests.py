from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Usuario
from .models import Credito


class CreditoViewTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.user = Usuario.objects.create_user(username='alumno', password='pass')
		self.admin = Usuario.objects.create_user(username='admin', password='pass', is_staff=True)

	def test_limit_five_credits_for_student(self):
	
		for i in range(5):
			Credito.objects.create(alumno=self.user, nombre=f'C{i}', tipo='academico', semestre='1')

		self.client.login(username='alumno', password='pass')
		resp = self.client.post(reverse('crear_credito'), {'nombre': 'Nuevo', 'tipo': 'academico', 'semestre': '1'})
		self.assertRedirects(resp, reverse('mis_creditos'))
		self.assertEqual(Credito.objects.filter(alumno=self.user).count(), 5)

	def test_admin_can_create_credit_for_user(self):
		self.client.login(username='admin', password='pass')
		resp = self.client.post(reverse('crear_credito'), {'alumno_id': self.user.id, 'nombre': 'AdminC', 'tipo': 'cultural', 'semestre': '2'})
		self.assertRedirects(resp, reverse('mis_creditos'))
		self.assertTrue(Credito.objects.filter(alumno=self.user, nombre='AdminC').exists())
