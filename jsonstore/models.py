#!/usr/bin/env python

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.contrib.postgres.fields import JSONField
from mptt.models import MPTTModel, TreeForeignKey

class JsonLedger(MPTTModel):
	hash_sum = models.CharField(max_length=64,unique=True,editable=False)
	data = JSONField()
	parent = TreeForeignKey('self',null=True, blank=True, on_delete=models.SET_NULL, related_name='children', db_index=True)

	def __str__(self):
		return self.hash_sum

class JsonTransaction(MPTTModel):
	hash_sum = models.CharField(max_length=64,unique=True,editable=False)
	data = JSONField()
	parent = TreeForeignKey('self',null=True, blank=True, on_delete=models.SET_NULL, related_name='children', db_index=True)

	def __str__(self):
		return self.hash_sum


@receiver(pre_save, sender=JsonLedger)
def pre_save_transaction(sender, instance, **kwargs):
	pass

@receiver(pre_save, sender=JsonTransaction)
def pre_save_transaction(sender, instance, **kwargs):
	pass
