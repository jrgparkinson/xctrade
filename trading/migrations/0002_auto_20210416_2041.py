# Generated by Django 3.1.7 on 2021-04-16 20:41

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trading', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entity',
            name='capital',
            field=models.DecimalField(decimal_places=2, default=100, max_digits=10),
        ),
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('interest_last_added', models.DateTimeField(null=True)),
                ('interest_rate', models.DecimalField(decimal_places=2, help_text='Fractional interest rate', max_digits=10)),
                ('interest_interval', models.DurationField(default=datetime.timedelta(7))),
                ('balance', models.DecimalField(decimal_places=2, max_digits=10)),
                ('lender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trading_loan_lender', to='trading.entity')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trading_loan_recipient', to='trading.entity')),
            ],
        ),
    ]
