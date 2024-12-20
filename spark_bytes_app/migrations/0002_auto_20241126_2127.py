# Generated by Django 3.2.5 on 2024-11-26 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spark_bytes_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='allergies',
            field=models.TextField(blank=True, help_text='List of common allergens to be aware of', null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='food_items',
            field=models.TextField(blank=True, help_text='List of food items available at the event', null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='food_types',
            field=models.CharField(blank=True, help_text='Types of food available (e.g., vegetarian, vegan, non-veg)', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='reserved_by',
            field=models.ManyToManyField(blank=True, related_name='reserved_events', to='spark_bytes_app.Profile'),
        ),
    ]
