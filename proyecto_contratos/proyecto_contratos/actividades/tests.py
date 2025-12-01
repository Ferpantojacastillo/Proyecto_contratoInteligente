from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Usuario
from .models import Actividad


class ActividadPermissionsTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.user = Usuario.objects.create_user(username='user1', password='pass')
		self.admin = Usuario.objects.create_user(username='admin', password='pass', is_staff=True)
		self.actividad = Actividad.objects.create(nombre='Act1', tipo='academico', fecha='2025-12-01T10:00:00')

	def test_only_admin_or_owner_can_liberar(self):
		
		self.client.login(username='user1', password='pass')
		resp = self.client.get(reverse('liberar_actividad', args=[self.actividad.id]))
		
		self.assertEqual(resp.status_code, 302)

		
		self.client.login(username='admin', password='pass')
		resp = self.client.get(reverse('liberar_actividad', args=[self.actividad.id]))
		self.assertEqual(resp.status_code, 302)
		self.actividad.refresh_from_db()
		self.assertTrue(self.actividad.liberado)
