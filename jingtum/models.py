#!/usr/bin/env python

from django.db import models
from django.contrib.auth.models import User
import re, subprocess, pprint, json
from decimal import Decimal
import datetime
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

class Result(models.Model):
	name = models.CharField(max_length=16,unique=True,)

	def __str__(self):
		return self.name


class Direction(models.Model):
	name = models.CharField(max_length=16,unique=True)

	def __str__(self):
		return self.name


class Wallet(models.Model):
	address = models.CharField(max_length=128,unique=True,)
	secret = models.CharField(max_length=128,blank=True,default='',)

	class Meta:
		verbose_name = '井通钱包'
		verbose_name_plural = '井通钱包'
		ordering = ('address', )

	def __str__(self):
		return self.address

	def sync_transactions(self):
		marker = {}
		results_per_page = 200
		page = 1
		has_more = True
		ledger_limit = 8000000
		page_limit = 50

		if not self.agent_set.all():
			raise ValueError("no agent associated")
		agent = self.agent_set.all().first()

		while has_more and page < page_limit:
			if 'ledger' in marker.keys():
				out = json.loads(subprocess.check_output("http 'https://api.jingtum.com/v2/accounts/%s/transactions?results_per_page=%s&marker={ledger:%s,seq:%s}'" % (self.address, results_per_page, marker['ledger'], marker['seq']),shell=True).decode())
			else:
				out = json.loads(subprocess.check_output("http 'https://api.jingtum.com/v2/accounts/%s/transactions?results_per_page=%s'" % (self.address, results_per_page),shell=True).decode())
			if 'marker' in out.keys():
				marker = out['marker']
			else:
				marker = {}
				has_more = False
			if 'transactions' not in out.keys():
				has_more = False
				break
			else:
				if len(out['transactions']) < results_per_page:
					has_more = False
			transactions = list(filter(lambda x: 'type' in x.keys() and 'result' in x.keys() and 'amount' in x.keys() and 'memos' in x.keys() and type(x['amount']) == type({}) and x['result'] == 'tesSUCCESS' and 'currency' in x['amount'].keys() and 'issuer' in x['amount'].keys() and (x['amount']['currency'] == 'SWT' or (x['amount']['currency'] == 'CNY' and x['amount']['issuer'] == 'jaNg3d59VHUiZ2eV4ZSH4Qyh9hUdAjDrzA')), out['transactions']))
			for transaction in transactions:
				print("%s\t%s" % (transaction['hash'], transaction['memos']))
				trans, created = Transaction.objects.get_or_create(hash_sum=transaction['hash'])
				if created:
					trans.agent = agent
					currency, created = Currency.objects.get_or_create(name=transaction['amount']['currency'], issuer=transaction['amount']['issuer'])
					counterparty, created = Wallet.objects.get_or_create(address=transaction['counterparty'])
					result, created = Result.objects.get_or_create(name=transaction['result'])
					direction, created = Direction.objects.get_or_create(name=transaction['type'])
					trans.currency = currency
					trans.amount = Decimal(transaction['amount']['value'])
					trans.counterparty = counterparty
					trans.date_int = transaction['date']
					trans.memos = ' '.join(transaction['memos'])[:128]
					trans.result = result
					trans.direction = direction
					trans.save()
			page += 1
			print(page)

	def sync_balances(self):
		pass


class Currency(models.Model):
	name = models.CharField(max_length=64,)
	issuer = models.CharField(max_length=64,default='',editable=False,)

	class Meta:
		verbose_name = '通证'
		verbose_name_plural = '通证'
		ordering = ('name', )
		unique_together = ('name', 'issuer')

	def __str__(self):
		return '%s/%s' % (self.name, self.issuer)


class Agent(models.Model):
	name = models.CharField(max_length=32,unique=True,)
	wallet = models.ForeignKey(Wallet, on_delete=models.PROTECT)
	user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True,blank=True,default=None)

	class Meta:
		verbose_name = '代理'
		verbose_name_plural = '代理'
		ordering = ('name', )

	def __str__(self):
		return self.name


class Transaction(models.Model):
	hash_sum = models.CharField(max_length=64,unique=True,editable=False,)
	currency = models.ForeignKey(Currency, on_delete=models.PROTECT,editable=False,default=None,null=True)
	amount = models.DecimalField(max_digits=20,decimal_places=8,editable=False,default=Decimal(0))
	counterparty = models.ForeignKey(Wallet, on_delete=models.PROTECT,null=True,default=None,editable=False,)
	date_int = models.IntegerField(default=0,editable=False)
	date = models.DateField(editable=False,null=True)
	memos = models.CharField(max_length=128,blank=True,default='',)
	result = models.ForeignKey(Result,on_delete=models.PROTECT,editable=False,default=None,null=True)
	direction = models.ForeignKey(Direction, on_delete=models.PROTECT, null=True, editable=False,default=None)
	deposite = models.BooleanField(verbose_name='代理充值',default=False,)
	lock_deposite = models.BooleanField(default=False,editable=False,)
	withdraw = models.BooleanField(verbose_name='代理回血',default=False,)
	lock_withdraw = models.BooleanField(default=False,editable=False,)
	activation = models.BooleanField(verbose_name='账号激活',default=False,editable=False,)
	agent = models.ForeignKey(Agent, on_delete=models.PROTECT,editable=False,default=None, null=True)

	class Meta:
		verbose_name = '交易记录'
		verbose_name_plural = '交易记录'
		ordering = ('-date_int', )

	def __str__(self):
		return self.hash_sum


@receiver(pre_save, sender=Transaction)
def pre_save_transaction(sender, instance, **kwargs):
	if instance.date_int:
		if not instance.date:
			instance.date = datetime.datetime.fromtimestamp(instance.date_int).date()
	if not instance.lock_deposite:
		if instance.currency:
			if instance.currency.name == 'CNY':
				if re.match('.*D[0-9]{15}', instance.memos, re.I):
					instance.lock_deposite = True
					instance.deposite = True
	if not instance.lock_withdraw:
		if instance.counterparty:
			if instance.counterparty.address == 'jaNg3d59VHUiZ2eV4ZSH4Qyh9hUdAjDrzA':
				if 'c2c' == instance.memos or instance.amount == Decimal(400000) or instance.amount == Decimal(500000):
					instance.lock_withdraw = True
					instance.withdraw = True
