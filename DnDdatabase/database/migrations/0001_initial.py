# Generated by Django 3.0.1 on 2020-08-31 20:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('group', models.CharField(blank=True, max_length=200)),
                ('hp_max', models.PositiveSmallIntegerField()),
                ('mana_max', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'Entities',
            },
        ),
        migrations.CreateModel(
            name='Skills',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('boj', models.SmallIntegerField(blank=True, null=True, verbose_name='boj')),
                ('sila', models.SmallIntegerField(blank=True, null=True, verbose_name='síla')),
                ('houzevnatost', models.SmallIntegerField(blank=True, null=True, verbose_name='houževnatost')),
                ('remeslo', models.SmallIntegerField(blank=True, null=True, verbose_name='řemeslo')),
                ('vira', models.SmallIntegerField(blank=True, null=True, verbose_name='víra')),
                ('obratnost', models.SmallIntegerField(blank=True, null=True, verbose_name='obratnost')),
                ('presnost', models.SmallIntegerField(blank=True, null=True, verbose_name='přesnost')),
                ('plizeni', models.SmallIntegerField(blank=True, null=True, verbose_name='plížení')),
                ('priroda', models.SmallIntegerField(blank=True, null=True, verbose_name='příroda')),
                ('zrucnost', models.SmallIntegerField(blank=True, null=True, verbose_name='zručnost')),
                ('magie', models.SmallIntegerField(blank=True, null=True, verbose_name='magie')),
                ('intelekt', models.SmallIntegerField(blank=True, null=True, verbose_name='intelekt')),
                ('znalosti', models.SmallIntegerField(blank=True, null=True, verbose_name='znalosti')),
                ('vnimani', models.SmallIntegerField(blank=True, null=True, verbose_name='vnímání')),
                ('charisma', models.SmallIntegerField(blank=True, null=True, verbose_name='charisma')),
                ('entity', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='database.Entity')),
            ],
            options={
                'verbose_name_plural': 'Skills lists',
            },
        ),
        migrations.CreateModel(
            name='Resistances',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acid', models.SmallIntegerField(default=0)),
                ('blunt', models.SmallIntegerField(default=0)),
                ('elemental', models.SmallIntegerField(default=0)),
                ('fire', models.SmallIntegerField(default=0)),
                ('ice', models.SmallIntegerField(default=0)),
                ('lightning', models.SmallIntegerField(default=0)),
                ('magic', models.SmallIntegerField(default=0)),
                ('necrotic', models.SmallIntegerField(default=0)),
                ('physical', models.SmallIntegerField(default=0)),
                ('piercing', models.SmallIntegerField(default=0)),
                ('poison', models.SmallIntegerField(default=0)),
                ('radiant', models.SmallIntegerField(default=0)),
                ('slashing', models.SmallIntegerField(default=0)),
                ('water', models.SmallIntegerField(default=0)),
                ('wind', models.SmallIntegerField(default=0)),
                ('entity', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='database.Entity')),
            ],
            options={
                'verbose_name_plural': 'Resistances lists',
            },
        ),
    ]
