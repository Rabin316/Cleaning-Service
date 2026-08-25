from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from django.urls import reverse

from config.settings import _parse_csv, _validate_production_settings
from .models import Booking, FavoriteService, Service


@override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False)
class ApplicationRegressionTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username='customer',
			password='correct-password',
			first_name='Test',
			last_name='Customer',
			email='customer@example.com',
		)
		self.service = Service.objects.create(
			name='Standard Clean',
			description='A standard clean',
			short_description='Standard cleaning',
			price_starting='125.00',
			duration='2 hours',
			features='Floors',
		)
		self.other_service = Service.objects.create(
			name='Deep Clean',
			description='A deep clean',
			short_description='Deep cleaning',
			price_starting='250.00',
			duration='4 hours',
			features='Everything',
		)

	def booking_data(self, service):
		return {
			'service': service.pk,
			'name': 'Test Customer',
			'email': 'customer@example.com',
			'phone': '5551234567',
			'address': '123 Main Street',
			'preferred_date': '2030-01-02',
			'preferred_time': '10:00',
			'frequency': 'one_time',
			'special_instructions': '',
		}

	def test_csv_settings_are_trimmed_and_empty_values_removed(self):
		self.assertEqual(
			_parse_csv(' https://example.com, ,https://admin.example.com '),
			['https://example.com', 'https://admin.example.com'],
		)

	def test_production_settings_reject_wildcard_hosts_and_origins(self):
		with self.assertRaisesMessage(ImproperlyConfigured, 'ALLOWED_HOSTS'):
			_validate_production_settings(False, ['*'], [])
		with self.assertRaisesMessage(ImproperlyConfigured, 'CSRF_TRUSTED_ORIGINS'):
			_validate_production_settings(False, ['example.com'], ['*'])

	def test_health_check_does_not_expose_database_error(self):
		response = self.client.get(reverse('health'))
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['status'], 'healthy')
		self.assertNotIn('error', response.json())

	def test_login_rejects_external_next_url(self):
		response = self.client.post(
			reverse('customer_login') + '?next=https://attacker.example/',
			{'username': 'customer', 'password': 'correct-password', 'next': 'https://attacker.example/'},
		)
		self.assertRedirects(response, reverse('customer_dashboard'))

	def test_favorite_removal_requires_post(self):
		self.client.force_login(self.user)
		FavoriteService.objects.create(user=self.user, service=self.service)
		url = reverse('toggle_favorite', args=[self.service.pk])
		self.assertEqual(self.client.get(url).status_code, 405)
		self.assertEqual(self.client.post(url).status_code, 200)
		self.assertFalse(FavoriteService.objects.filter(user=self.user, service=self.service).exists())

	@override_settings(DEBUG=True)
	def test_quick_booking_uses_route_service_and_server_amount(self):
		self.client.force_login(self.user)
		response = self.client.post(
			reverse('quick_booking', args=[self.service.pk]),
			self.booking_data(self.other_service),
		)
		self.assertRedirects(response, reverse('booking_detail', args=[Booking.objects.latest('id').pk]))
		booking = Booking.objects.latest('id')
		self.assertEqual(booking.service_id, self.service.pk)
		self.assertEqual(booking.amount, Decimal('125.00'))
		self.assertEqual(booking.payment_status, 'paid')

	@override_settings(DEBUG=False, STRIPE_SECRET_KEY='sk_test_local')
	@patch('cleaning.views.create_payment_intent')
	def test_booking_returns_client_secret_for_created_intent(self, create_intent):
		create_intent.return_value = SimpleNamespace(id='pi_test', client_secret='secret_test')
		response = self.client.post(reverse('booking'), self.booking_data(self.service))
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['client_secret'], 'secret_test')
		create_intent.assert_called_once()

	def test_custom_admin_urls_reverse(self):
		self.assertEqual(reverse('admin:dashboard'), '/admin/dashboard/')
		self.assertEqual(reverse('admin:dashboard_team_schedule'), '/admin/dashboard/team-schedule/')
		self.assertEqual(reverse('admin:dashboard_revenue'), '/admin/dashboard/revenue/')

	def test_rebook_requires_post_and_prefills_booking_form(self):
		self.client.force_login(self.user)
		old_booking = Booking.objects.create(
			user=self.user,
			service=self.service,
			name='Test Customer',
			email='customer@example.com',
			phone='5551234567',
			address='123 Main Street',
			preferred_date='2029-01-02',
			preferred_time='10:00',
			frequency='one_time',
			status='completed',
		)
		url = reverse('rebook', args=[old_booking.pk])
		self.assertEqual(self.client.get(url).status_code, 405)
		response = self.client.post(url)
		self.assertRedirects(response, reverse('booking'))
		booking_page = self.client.get(reverse('booking'))
		self.assertContains(booking_page, f'value="{self.service.pk}"')
		self.assertContains(booking_page, old_booking.address)
		response = self.client.post(reverse('booking'), self.booking_data(self.service))
		self.assertRedirects(response, reverse('booking_success'))
		self.assertNotIn('rebook_data', self.client.session)

	def test_invalid_ajax_booking_returns_json_error(self):
		response = self.client.post(
			reverse('booking'),
			{},
			HTTP_X_REQUESTED_WITH='XMLHttpRequest',
		)
		self.assertEqual(response.status_code, 400)
		self.assertFalse(response.json()['success'])

	def test_customer_dashboard_renders_supplied_data(self):
		self.client.force_login(self.user)
		data = self.booking_data(self.service)
		data['service'] = self.service
		Booking.objects.create(user=self.user, **data)
		response = self.client.get(reverse('customer_dashboard'))
		self.assertContains(response, 'Upcoming Bookings')
		self.assertContains(response, self.service.name)
		self.assertContains(response, 'Completed Bookings')

	def test_customer_booking_statuses_use_explicit_classes(self):
		self.client.force_login(self.user)
		data = self.booking_data(self.service)
		data['service'] = self.service
		booking = Booking.objects.create(
			user=self.user,
			**data,
			status='completed',
		)
		response = self.client.get(reverse('booking_detail', args=[booking.pk]))
		self.assertContains(response, 'bg-success')
		self.assertNotContains(response, 'bg-completed')
