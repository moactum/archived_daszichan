#!/usr/bin/env python

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.contrib.postgres.fields import JSONField
from mptt.models import MPTTModel, TreeForeignKey
from urllib import request
import sys, random, time, json

class JsonLedger(models.Model):
	hash_sum = models.CharField(max_length=64,unique=True,editable=False)
	parent_hash = models.CharField(max_length=64,default='',unique=True,editable=False)
	data = JSONField()
	synced = models.BooleanField(default=False, editable=False)
	#parent = TreeForeignKey('self',null=True, blank=True, on_delete=models.SET_NULL, related_name='children', db_index=True)

	def __str__(self):
		return "%s: %s" % (self.id, self.hash_sum)
	@classmethod
	def sync(cls,hash_sum):
		url = "http://state.jingtum.com/query/ledger/%s" % hash_sum
		done = False
		try:
			ledger = cls.objects.get(hash_sum=hash_sum)
			done = True
		except cls.DoesNotExist:
			pass
		while not done:
			try:
				response = request.urlopen(url,timeout=90)
				if response.status == 200:
					result = json.loads(response.read().decode())
					summary = result['data']['data']['summary']
					parent_hash = summary['parent_hash']
					ledger = cls(id=int(summary['ledger_index']),hash_sum=hash_sum,parent_hash=parent_hash,data=result)
					ledger.save()
					done = True
				else:
					out = sys.stdout.write("..!..http returned status %s\n" % response.status)
					time.sleep(10 * random.randint(1,10))
			except Exception as e:
				out = sys.stderr.write("exception happend\n")
				print(e)
				time.sleep(60 * random.randint(1,10))
		return ledger

class JsonTransaction(MPTTModel):
	hash_sum = models.CharField(max_length=64,unique=True,editable=False)
	data = JSONField()
	ledger = models.ForeignKey(JsonLedger, null=True, blank=True, default=None, editable=False, on_delete=models.SET_NULL)
	parent = TreeForeignKey('self',null=True, blank=True, on_delete=models.SET_NULL, related_name='children', db_index=True)

	def __str__(self):
		return self.id


@receiver(pre_save, sender=JsonLedger)
def pre_save_transaction(sender, instance, **kwargs):
	pass

@receiver(pre_save, sender=JsonTransaction)
def pre_save_transaction(sender, instance, **kwargs):
	pass
