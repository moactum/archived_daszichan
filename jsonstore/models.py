#!/usr/bin/env python

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.contrib.postgres.fields import JSONField
from mptt.models import MPTTModel, TreeForeignKey
from urllib import request
import sys, random, time, json
from moac.models import * 

class JsonJingtumLedger(models.Model):
	hash = models.CharField(max_length=64,unique=True,editable=False)
	parent_hash = models.CharField(max_length=64,default='',unique=True,editable=False)
	data = JSONField()
	synced = models.BooleanField(default=False, editable=False)
	#parent = TreeForeignKey('self',null=True, blank=True, on_delete=models.SET_NULL, related_name='children', db_index=True)

	def __str__(self):
		return "%s: %s" % (self.id, self.hash)

	@classmethod
	def sync(cls,hash):
		url = "http://state.jingtum.com/query/ledger/%s" % hash
		done = False
		try:
			ledger = cls.objects.get(hash=hash)
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
					ledger = cls(id=int(summary['ledger_index']),hash=hash,parent_hash=parent_hash,data=result)
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

class JsonJingtumTransaction(MPTTModel):
	hash = models.CharField(max_length=64,unique=True,editable=False)
	data = JSONField()
	ledger = models.ForeignKey(JsonJingtumLedger, null=True, blank=True, default=None, editable=False, on_delete=models.SET_NULL)
	parent = TreeForeignKey('self',null=True, blank=True, on_delete=models.SET_NULL, related_name='children', db_index=True)

	def __str__(self):
		return self.hash

class JsonMoacLedger(models.Model):
	hash = models.CharField(max_length=66,unique=True,editable=False)
	parent_hash = models.CharField(max_length=66,default='',unique=True,editable=False)
	data = JSONField()
	synced = models.BooleanField(default=False, editable=False)
	#parent = TreeForeignKey('self',null=True, blank=True, on_delete=models.SET_NULL, related_name='children', db_index=True)

	class Meta:
		ordering = ('id',)
	def __str__(self):
		return "%s: %s" % (self.id, self.hash)

	def delete(self):
		for l in Ledger.objects.filter(number=self.id):
			l.delete()
		super(JsonMoacLedger,self).delete()

	def proc_ledger(self,do_uncle=False):
		try:
			ledger = Ledger.objects.get(hash=self.hash)
			if do_uncle:
				for uncle_hash in self.data['uncles']:
					uncle,created = Uncle.objects.get_or_create(hash=uncle_hash,ledger=ledger)
		except Ledger.DoesNotExist:
			miner,created = Address.objects.get_or_create(address=self.data['miner'])
			if created:
				miner.update_display()
			num_txs = len(self.data['transactions'])
			tps = int(num_txs / (self.data['timestamp'] - JsonMoacLedger.objects.get(id=self.id - 1).data['timestamp']))
			ledger = Ledger(hash=self.hash, number=self.id, num_txs=num_txs, tps=tps, difficulty = self.data['difficulty'], nonce = self.data['nonce'], miner=miner, timestamp=self.data['timestamp'])
			ledger.save()
			if self.data['transactions']:
				for txr in self.data['transactions']:
					sys.stdout.write("%s, " % txr['transactionIndex'])
					tx_from, created = Address.objects.get_or_create(address=txr['from'])
					if created:
						tx_from.update_display()
					if txr['to']:
						tx_to, created = Address.objects.get_or_create(address=txr['to'])
						if created:
							tx_to.update_display()
					else:
						tx_to = None
					transaction, created = Transaction.objects.get_or_create(ledger=ledger,hash=txr['hash'],tx_from=tx_from, tx_to=tx_to, value=int(float(txr['value'])) / 1000000000)
					transaction.save()
				sys.stdout.write('\n')
			for uncle_hash in self.data['uncles']:
				uncle,created = Uncle.objects.get_or_create(hash=uncle_hash,ledger=ledger)
			
	@classmethod
	def verify(cls,start=0):
		last = cls.objects.get(id=start)
		for jml in cls.objects.filter(id__gt=start):
			if jml.parent_hash != last.hash:
				print(jml)
				print(last)
				if last.id != jml.id - 1:
					print("\t...trying to sync missing ledgers")
					id_to_sync = last.id + 1
					while id_to_sync < jml.id:
						cls.sync(id_to_sync)
						id_to_sync += 1
				else:
					print("\tparent:%s" % jml.parent_hash)
					print("\tparent:%s" % last.hash)
			last = jml
		return True

	@classmethod
	def sync(cls,height,url=''):
		if not url:
			url = "http://localhost:3003/api/block/%s" % height
		done = False
		try:
			last = cls.objects.get(id=height-1)
			ledger = cls.objects.get(id=height)
			done = True
			if ledger.parent_hash != last.hash:
				sys.stdout.write("\tinconsistancy found, delete last two")
				last.delete()
				ledger.delete()
				ledger = cls.objects.get(id=height-2)
		except cls.DoesNotExist:
			pass
		while not done:
			try:
				response = request.urlopen(url,timeout=30)
				if response.status == 200:
					result = json.loads(response.read().decode())
					hash = result['hash']
					parent_hash = result['parentHash']
					if parent_hash == last.hash:
						ledger = cls(id=height,hash=hash,parent_hash=parent_hash,data=result)
						ledger.save()
					else:
						sys.stdout.write("\tinconsistancy found, delete last two")
						last.delete()
						ledger = cls.objects.get(id=height-2)
					done = True
				else:
					out = sys.stdout.write("..!..http returned status %s\n" % response.status)
					time.sleep(random.randint(5,10))
			except Exception as e:
				out = sys.stderr.write("exception happend\n")
				print(e)
				time.sleep(random.randint(5,10))
		sys.stdout.write("\tsynced %s" % height)
		return ledger

class JsonMoacTransaction(MPTTModel):
	hash = models.CharField(max_length=64,unique=True,editable=False)
	data = JSONField()
	ledger = models.ForeignKey(JsonMoacLedger, null=True, blank=True, default=None, editable=False, on_delete=models.SET_NULL)
	parent = TreeForeignKey('self',null=True, blank=True, on_delete=models.SET_NULL, related_name='children', db_index=True)

	def __str__(self):
		return self.hash

@receiver(pre_save, sender=JsonJingtumLedger)
def pre_save_ledger_jingtum(sender, instance, **kwargs):
	pass

@receiver(pre_save, sender=JsonMoacLedger)
def pre_save_ledger_moac(sender, instance, **kwargs):
	pass

@receiver(post_save, sender=JsonMoacLedger)
def pre_save_ledger_moac(sender, instance, created, **kwargs):
	if created:
		instance.proc_ledger()
