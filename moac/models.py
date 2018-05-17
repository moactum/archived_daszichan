#!/usr/bin/env python

from django.db import models
import re, subprocess, pprint, json
from decimal import Decimal
import datetime
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
#from mptt.models import MPTTModel, TreeForeignKey
from django.utils import timezone

class Address(models.Model):
	id = models.BigAutoField(primary_key=True)
	address = models.CharField(max_length=43,unique=True,default='0x')
	display = models.CharField(max_length=16,default='')

	class Meta:
		ordering = ('address', )

	def __str__(self):
		return self.display
	def update_display(self):
		if not self.display:
			self.display = "addr-%08d"  % self.id
			self.save()

class Ledger(models.Model):
	hash = models.CharField(max_length=66,primary_key=True)
	number = models.IntegerField("hight",default=0)
	num_txs = models.IntegerField(default=0)
	tps = models.IntegerField(default=0)
	difficulty = models.BigIntegerField(default=0)
	nonce = models.CharField(max_length=20,default='')
	timestamp = models.IntegerField(default=0)
	date = models.DateField(editable=False,null=True,default=None)
	miner = models.ForeignKey(Address, on_delete=models.PROTECT, editable=False,default=None, null=True)
	#parent = TreeForeignKey('self',null=True, blank=True, on_delete=models.SET_NULL, related_name='children', db_index=True)

	class Meta:
		ordering = ('number',)

	def __str__(self):
		return self.hash

class StatLedger(models.Model):
	date = models.DateField(editable=False,unique=True)
	ledger_txs = models.ForeignKey(Ledger, on_delete=models.SET_NULL, null=True, default=None, editable=False, related_name="ledger_txs")
	ledger_tps = models.ForeignKey(Ledger, on_delete=models.SET_NULL, null=True, default=None, editable=False, related_name="ledger_tps")

class Transaction(models.Model):
	hash = models.CharField(max_length=66,primary_key=True)
	tx_from = models.ForeignKey(Address,related_name='txs_sent', on_delete=models.PROTECT, editable=False, default=None, null=True)
	tx_to = models.ForeignKey(Address,related_name='txs_recv', on_delete=models.PROTECT, editable=False, default=None, null=True)
	value = models.BigIntegerField(default=0)
	index = models.IntegerField(default=0)
	ledger = models.ForeignKey(Ledger, on_delete=models.CASCADE, editable=False,default=None, null=True)

	class Meta:
		ordering = ('ledger','index')

	def __str__(self):
		return self.hash
	
@receiver(pre_save, sender=Ledger)
def pre_save_ledger(sender, instance, **kwargs):
	if not instance.date:
		instance.date = timezone.make_aware(timezone.datetime.fromtimestamp(instance.timestamp)).date()

@receiver(post_save, sender=Ledger)
def post_save_transaction_moac(sender, instance, created, **kwargs):
	if created:
		statledger,created = StatLedger.objects.get_or_create(date=instance.date)
		if not statledger.ledger_txs or stateledger.ledger_txs.num_txs < instance.num_txs:
			statledger.ledger_txs = instance
			statledger.save()
		if not statledger.ledger_tps or stateledger.ledger_tps.tps < instance.tps:
			statledget.ledger_tps = instance
			statledger.save()
@receiver(pre_save, sender=Address)
def pre_save_address(sender, instance, **kwargs):
	pass
