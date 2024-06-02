# Generated by Django 5.0.2 on 2024-03-12 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Hospital',
            fields=[
                ('h_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256)),
                ('email', models.EmailField(max_length=256)),
                ('h_lattitude', models.FloatField(blank=True, null=True)),
                ('h_longitude', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('n_id', models.AutoField(primary_key=True, serialize=False)),
                ('notification', models.CharField(max_length=1000)),
                ('accident_date', models.DateTimeField(auto_now_add=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('accepted', models.IntegerField(blank=True, null=True)),
            ],
        ),
    ]