# Generated migration file for adding Stripe payment fields to Booking model
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cleaning', '0003_remove_customerprofile_loyalty_points_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            "UPDATE cleaning_booking SET payment_intent_id = '' WHERE payment_intent_id IS NULL; "
            "UPDATE cleaning_booking SET customer_review = '' WHERE customer_review IS NULL; "
            "UPDATE cleaning_booking SET special_instructions = '' WHERE special_instructions IS NULL",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.AlterField(
            model_name='booking',
            name='payment_intent_id',
            field=models.CharField(blank=True, help_text='Stripe Payment Intent ID', max_length=255),
        ),
        migrations.AddField(
            model_name='booking',
            name='amount_paid',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Amount actually paid', max_digits=10),
        ),
        migrations.AddField(
            model_name='booking',
            name='currency',
            field=models.CharField(default='usd', help_text='Currency code (usd, eur, etc.)', max_length=3),
        ),
        migrations.AddField(
            model_name='booking',
            name='stripe_charge_id',
            field=models.CharField(blank=True, default='', help_text='Stripe Charge ID after payment', max_length=255),
            preserve_default=False,
        ),
    ]