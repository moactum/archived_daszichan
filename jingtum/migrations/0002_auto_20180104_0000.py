# Generated by Django 2.0 on 2018-01-04 00:00

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('jingtum', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('user', models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '代理',
                'verbose_name_plural': '代理',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('issuer', models.CharField(default='', editable=False, max_length=64)),
            ],
            options={
                'verbose_name': '通证',
                'verbose_name_plural': '通证',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Direction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash_sum', models.CharField(editable=False, max_length=64, unique=True)),
                ('amount', models.DecimalField(decimal_places=8, default=Decimal('0'), editable=False, max_digits=20)),
                ('date_int', models.IntegerField(default=0, editable=False)),
                ('date', models.DateField(editable=False, null=True)),
                ('memos', models.CharField(blank=True, default='', max_length=128)),
                ('deposite', models.BooleanField(default=False, verbose_name='代理充值')),
                ('lock_deposite', models.BooleanField(default=False, editable=False)),
                ('withdraw', models.BooleanField(default=False, verbose_name='代理回血')),
                ('lock_withdraw', models.BooleanField(default=False, editable=False)),
                ('activation', models.BooleanField(default=False, editable=False, verbose_name='账号激活')),
                ('agent', models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, to='jingtum.Agent')),
            ],
            options={
                'verbose_name': '交易记录',
                'verbose_name_plural': '交易记录',
                'ordering': ('-date_int',),
            },
        ),
        migrations.AlterModelOptions(
            name='wallet',
            options={'ordering': ('address',), 'verbose_name': '井通钱包', 'verbose_name_plural': '井通钱包'},
        ),
        migrations.AlterField(
            model_name='wallet',
            name='address',
            field=models.CharField(max_length=128, unique=True),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='secret',
            field=models.CharField(blank=True, default='', max_length=128),
        ),
        migrations.AddField(
            model_name='transaction',
            name='counterparty',
            field=models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, to='jingtum.Wallet'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='currency',
            field=models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, to='jingtum.Currency'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='direction',
            field=models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, to='jingtum.Direction'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='result',
            field=models.ForeignKey(default=None, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, to='jingtum.Result'),
        ),
        migrations.AlterUniqueTogether(
            name='currency',
            unique_together={('name', 'issuer')},
        ),
        migrations.AddField(
            model_name='agent',
            name='wallet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='jingtum.Wallet'),
        ),
    ]
