from django.core.management.base import BaseCommand, CommandError
from jsonstore.models import * 
import sys, subprocess

class Command(BaseCommand):
	help = 'Sychronize json ledgers/transactions with provided ledger height and hash'

	def add_arguments(self,parser):
		parser.add_argument('--hash_sum', action="store", dest="hash_sum", help="specify the ledger hash, get from state.jingtum.com")

	def handle(self, *args, **options):
		if options['hash_sum']:
			hash_sum = options['hash_sum']
			self.stdout.write("...got arguments to synchronize ledger from %s" % hash_sum)
			try:
				ledger = JsonLedger.objects.get(hash_sum=hash_sum)
				hash_sum = ledger.parent_hash
				self.stdout.write("......bypassing %s, " % ledger.id, ending='')
			except JsonLedger.DoesNotExist:
				pass
			self.stdout.write("")
			ledger = JsonLedger.sync(hash_sum)
			self.stdout.write("......synced ledger %s" % ledger.id)
			while ledger and ledger.parent_hash and ledger.id % 1000000:
				self.stdout.write("...... syncing %s ... " % ledger.parent_hash, ending='')
				ledger = JsonLedger.sync(ledger.parent_hash)
				self.stdout.write("synced ledger %s" % ledger.id)
		else:
			self.stdout.write("...not arguments, try to continuing syching ledger")
			ledger_starting = JsonLedger.objects.all().order_by('id').first()
			if not ledger_starting:
				self.stdout.write("......please provide initial conditions to sync ledger")
			elif ledger_starting.id == 1:
				self.stdout.write("......already synced ledger")
			elif ledger_starting.parent_hash:
				self.stdout.write("......starting sync with leger %s" % ledger_starting.parent_hash)
				ledger = JsonLedger.sync(ledger_starting.parent_hash)
				self.stdout.write("...... syncing ledger at %s" % ledger.id)
				while ledger and ledger.parent_hash:
					self.stdout.write("...... syncing %s ... " % ledger.parent_hash, ending='')
					ledger = JsonLedger.sync(ledger.parent_hash)
					self.stdout.write("synced ledger %s" % ledger.id)
			else:
					self.stdout.print("finished")
		self.stdout.write(self.style.SUCCESS('Successfully sychronized agents'))
