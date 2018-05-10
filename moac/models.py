#!/usr/bin/env python

from django.db import models
import re, subprocess, pprint, json
from decimal import Decimal
import datetime
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from mptt.models import MPTTModel, TreeForeignKey

class Ledger(models.Model):
	hash = models.CharField(max_length=64,unique=True,editable=False,)
	num_txs = models.IntegerField(default=0,editable=False)
	#parent = TreeForeignKey('self',null=True, blank=True, on_delete=models.SET_NULL, related_name='children', db_index=True)

	def __str__(self):
		return self.hash_sum

class Transaction(models.Model):
	hash = models.CharField(max_length=64,unique=True,editable=False,)
	parent = TreeForeignKey('self',null=True, blank=True, on_delete=models.SET_NULL, related_name='children', db_index=True)
	synced = models.BooleanField(default=False,editable=False,)
	ledger = models.ForeignKey(Ledger, on_delete=models.PROTECT, editable=False,default=None, null=True)

	class Meta:
		pass
		#ordering = ('-date_int', )

	def __str__(self):
		return self.hash_sum

class Currency(models.Model):
	name = models.CharField(max_length=64,)
	issuer = models.CharField(max_length=64,default='',editable=False,)

	class Meta:
		ordering = ('name', )
		unique_together = ('name', 'issuer')

	def __str__(self):
		return self.name
	
class Wallet(models.Model):
	address = models.CharField(max_length=128,unique=True,)
	secret = models.CharField(max_length=128,blank=True,default='',)

	class Meta:
		ordering = ('address', )

	def __str__(self):
		#return "%s***%s" % (self.address[:5], self.address[-5:])
		return self.address

	def sync_transactions(self, leger_limit=8000000, page_limit=2000, datetime_limit=datetime.datetime(2017,12,1)):
		pass

	def sync_balances(self):
		pass

class Agent(models.Model):
	name = models.CharField(max_length=32,unique=True,)
	wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True,blank=True,default=None)
	user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True,blank=True,default=None)

	class Meta:
		verbose_name = '代理'
		verbose_name_plural = '代理'
		ordering = ('name', )

	def __str__(self):
		return self.name


#	currency = models.ForeignKey(Currency,verbose_name="通证",on_delete=models.PROTECT,editable=False,default=None,null=True)
#	amount = models.DecimalField("数额",max_digits=20,decimal_places=8,editable=False,default=Decimal(0))
#	counterparty = models.ForeignKey(Wallet, verbose_name="对家", on_delete=models.PROTECT,null=True,default=None,editable=False,)
#	date_int = models.IntegerField(default=0,editable=False)
#	date = models.DateField(editable=False,null=True)
#	memos = models.CharField("留言", max_length=128,blank=True,default='',)
#	result = models.ForeignKey(Result,on_delete=models.PROTECT,editable=False,default=None,null=True)
#	direction = models.ForeignKey(Direction, verbose_name="类型", on_delete=models.PROTECT, null=True, editable=False,default=None)
#	deposite = models.BooleanField(verbose_name='充值',default=False,)
#	lock_deposite = models.BooleanField(default=False,editable=False,)
#	withdraw = models.BooleanField(verbose_name='回血',default=False,)
#	lock_withdraw = models.BooleanField(default=False,editable=False,)
#	activation = models.BooleanField(verbose_name='激活',default=False,editable=False,)
#	agent = models.ForeignKey(Agent,verbose_name='代理', on_delete=models.PROTECT,editable=False,default=None, null=True)

#@receiver(pre_save, sender=Transaction)
#def pre_save_transaction(sender, instance, **kwargs):
#	if instance.date_int:
#		if not instance.date:
#			instance.date = datetime.datetime.fromtimestamp(instance.date_int).date()
#	if not instance.lock_deposite:
#		if instance.currency and instance.currency.name == 'CNY' and re.match('.*D[0-9]{15}', instance.memos, re.I):
#			instance.lock_deposite = True
#			instance.deposite = True
#	if not instance.lock_withdraw:
#		if instance.direction and instance.direction.name == 'received' and instance.currency and instance.currency.name == 'CNY' and instance.counterparty and (instance.counterparty.address == 'jaNg3d59VHUiZ2eV4ZSH4Qyh9hUdAjDrzA' or instance.counterparty.address == 'jU2YgNfRcTghKJXWTTWNMBpPnmXhyihEpn' ):
#			if 'c2c' == instance.memos or (instance.amount == Decimal(400000) or instance.amount == Decimal(500000) or instance.amount == Decimal(50000)):
#				instance.lock_withdraw = True
#				instance.withdraw = True
