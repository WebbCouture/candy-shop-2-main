# FINAL FIX – gift fields for purchase history
from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_order_gift_amount_order_gift_code_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='gift_amount',
            field=models.DecimalField(
                default=Decimal('0.00'),
                decimal_places=2,
                max_digits=10,
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='gift_recipient',
            field=models.CharField(
                blank=True,
                default='',
                max_length=200,
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='gift_code',
            field=models.CharField(
                blank=True,
                default='',
                max_length=50,
            ),
        ),
    ]