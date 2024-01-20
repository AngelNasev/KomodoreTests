# Generated by Django 4.2.4 on 2023-08-27 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('KomodoreApp', '0008_order_payment_method_order_payment_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_address',
            field=models.CharField(default='Django Street', max_length=150),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_city',
            field=models.CharField(default='Los Angeles', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_country',
            field=models.CharField(default='USA', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_note',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_postal_code',
            field=models.CharField(default='90001', max_length=20),
            preserve_default=False,
        ),
    ]