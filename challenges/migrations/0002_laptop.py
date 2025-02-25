# Generated by Django 4.2.3 on 2024-02-28 06:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Laptop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand', models.CharField(choices=[('HP', 'HP'), ('DELL', 'Dell'), ('LENOVO', 'Lenovo'), ('ASUS', 'Asus'), ('ACER', 'Acer')], max_length=256)),
                ('year', models.IntegerField()),
                ('memory', models.IntegerField()),
                ('disk', models.IntegerField()),
                ('price', models.FloatField()),
                ('count', models.IntegerField()),
                ('created_at', models.DateTimeField()),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
