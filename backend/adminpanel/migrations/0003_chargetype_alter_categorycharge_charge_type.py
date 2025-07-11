# Generated by Django 4.2 on 2025-07-02 06:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0002_categorycharge'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChargeType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('code', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.AlterField(
            model_name='categorycharge',
            name='charge_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminpanel.chargetype'),
        ),
    ]
