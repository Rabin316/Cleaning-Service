"""
Stripe Utility Functions for Cleaning Service Payment Processing
"""
import stripe
import logging
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views import View
from .models import Booking

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')


def create_payment_intent(booking):
    """
    Create a Stripe Payment Intent for a booking
    """
    try:
        # Convert amount to cents (Stripe expects smallest currency unit)
        amount_cents = int(booking.amount * 100)

        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=booking.currency,
            metadata={
                'booking_id': booking.id,
                'customer_name': booking.name,
                'customer_email': booking.email,
                'service_name': booking.service.name if booking.service else 'Unknown Service'
            },
            description=f"Cleaning Service Booking #{booking.id} - {booking.service.name if booking.service else 'Service'}",
            receipt_email=booking.email
        )

        # Save the payment intent ID to the booking
        booking.payment_intent_id = intent.id
        booking.save(update_fields=['payment_intent_id'])

        return intent

    except stripe.error.StripeError:
        logger.exception('Stripe payment intent failed for booking_id=%s', booking.id)
        raise
    except Exception:
        logger.exception('Payment intent creation failed for booking_id=%s', booking.id)
        raise


def confirm_payment(booking, payment_intent_id):
    """
    Confirm a payment intent and update booking status
    """
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        if intent.status == 'succeeded':
            # Update booking with successful payment
            booking.payment_status = 'paid'
            booking.amount_paid = booking.amount
            booking.stripe_charge_id = intent.charges.data[0].id if intent.charges.data else ''
            booking.save(update_fields=['payment_status', 'amount_paid', 'stripe_charge_id'])

            # Create notification for customer
            from .models import Notification
            if booking.user:
                Notification.objects.create(
                    user=booking.user,
                    title='Payment Successful',
                    message=f'Your payment of ${booking.amount:.2f} for booking #{booking.id} has been processed successfully.',
                    notification_type='booking'
                )

            return True, intent
        else:
            logger.warning(f"Payment intent {payment_intent_id} not succeeded. Status: {intent.status}")
            return False, intent

    except stripe.error.StripeError:
        logger.exception('Stripe payment confirmation failed for booking_id=%s', booking.id)
        # Update booking payment status to failed
        booking.payment_status = 'failed'
        booking.save(update_fields=['payment_status'])
        return False, None
    except Exception:
        logger.exception('Payment confirmation failed for booking_id=%s', booking.id)
        return False, None


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(View):
    """
    Handle Stripe webhooks for payment events
    """

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            # Invalid payload
            logger.warning('Invalid payload in Stripe webhook')
            return JsonResponse({'error': 'Invalid payload'}, status=400)
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            logger.warning('Invalid signature in Stripe webhook')
            return JsonResponse({'error': 'Invalid signature'}, status=400)

        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            self.handle_payment_intent_succeeded(payment_intent)
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            self.handle_payment_intent_failed(payment_intent)
        elif event['type'] == 'charge.refunded':
            charge = event['data']['object']
            self.handle_charge_refunded(charge)
        else:
            logger.info(f"Unhandled Stripe event type: {event['type']}")

        return JsonResponse({'status': 'success'})

    def handle_payment_intent_succeeded(self, payment_intent):
        """Handle successful payment"""
        booking_id = payment_intent.metadata.get('booking_id')
        if booking_id:
            try:
                booking = Booking.objects.get(id=booking_id)
                booking.payment_status = 'paid'
                booking.amount_paid = booking.amount
                booking.stripe_charge_id = payment_intent.charges.data[0].id if payment_intent.charges.data else ''
                booking.save(update_fields=['payment_status', 'amount_paid', 'stripe_charge_id'])

                # Create notification
                from .models import Notification
                if booking.user:
                    Notification.objects.create(
                        user=booking.user,
                        title='Payment Successful',
                        message=f'Your payment of ${booking.amount:.2f} for booking #{booking.id} has been processed successfully.',
                        notification_type='booking'
                    )
                logger.info(f"Payment succeeded for booking {booking_id}")
            except Booking.DoesNotExist:
                logger.error(f"Booking {booking_id} not found for successful payment intent")
            except Exception:
                logger.exception('Successful payment handling failed for booking_id=%s', booking_id)

    def handle_payment_intent_failed(self, payment_intent):
        """Handle failed payment"""
        booking_id = payment_intent.metadata.get('booking_id')
        if booking_id:
            try:
                booking = Booking.objects.get(id=booking_id)
                booking.payment_status = 'failed'
                booking.save(update_fields=['payment_status'])

                # Create notification
                from .models import Notification
                if booking.user:
                    Notification.objects.create(
                        user=booking.user,
                        title='Payment Failed',
                        message=f'Your payment for booking #{booking.id} has failed. Please try again or contact support.',
                        notification_type='booking'
                    )
                logger.info(f"Payment failed for booking {booking_id}")
            except Booking.DoesNotExist:
                logger.error(f"Booking {booking_id} not found for failed payment intent")
            except Exception:
                logger.exception('Failed payment handling failed for booking_id=%s', booking_id)

    def handle_charge_refunded(self, charge):
        """Handle refunded charge"""
        booking_id = charge.metadata.get('booking_id')
        if booking_id:
            try:
                booking = Booking.objects.get(id=booking_id)
                booking.payment_status = 'refunded'
                booking.save(update_fields=['payment_status'])

                # Create notification
                from .models import Notification
                if booking.user:
                    Notification.objects.create(
                        user=booking.user,
                        title='Payment Refunded',
                        message=f'Your payment for booking #{booking.id} has been refunded.',
                        notification_type='booking'
                    )
                logger.info(f"Charge refunded for booking {booking_id}")
            except Booking.DoesNotExist:
                logger.error(f"Booking {booking_id} not found for refunded charge")
            except Exception:
                logger.exception('Refund handling failed for booking_id=%s', booking_id)


def get_stripe_publishable_key():
    """Get Stripe publishable key for frontend"""
    return getattr(settings, 'STRIPE_PUBLISHABLE_KEY', '')