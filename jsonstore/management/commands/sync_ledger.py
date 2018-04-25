from django.core.management.base import BaseCommand, CommandError
from jsonstore.models import * 
import sys, subprocess
import json, pprint, datetime
import time, random

from socketIO_client import SocketIO, BaseNamespace

class Namespace(BaseNamespace):
	def on_connect(self):
		sys.stdout.write("...socketio service connected\n")
	def on_message(self,msg):
		msg = msg.decode()
		try:
			if int(msg[0]) == 2:
				#pprint.pprint(msg[1:])
				msg = json.loads(msg[1:])
				if msg[0] == "ledger_closed":
					sys.stdout.write("...... syncing %s ... " % msg[1][0]['ledger_hash'])
					ledger = JsonLedger.sync(msg[1][0]['ledger_hash'])
					sys.stdout.write("synced ledger %s\n" % ledger.id)
		except Exception as e:
			sys.stdout.write("...!... got exception ...")
			e


class Command(BaseCommand):
	help = 'Sychronize json ledgers/transactions with provided ledger height and hash'

	def add_arguments(self,parser):
		parser.add_argument('--hash_sum', action="store", dest="hash_sum", help="specify the ledger hash, get from state.jingtum.com")
		parser.add_argument('--websocket', action="store_true", dest="websocket", help="sync leger with websocket")
		parser.add_argument('--missing', action="store_true", dest="missing", help="sync missing leger")
		parser.add_argument('--onceonly', action="store_true", dest="onceonly", help="syncing onestop")

	def handle(self, *args, **options):
		if options['hash_sum']:
			hash_sum = options['hash_sum']
			self.stdout.write("...got arguments to synchronize ledger from %s" % hash_sum)
			if not options['onceonly']:
				try:
					self.stdout.write("......bypassing", ending='')
					while hash_sum:
						ledger = JsonLedger.objects.get(hash_sum=hash_sum)
						hash_sum = ledger.parent_hash
						self.stdout.write(" %s," % ledger.id, ending='')
				except JsonLedger.DoesNotExist:
					pass
				self.stdout.write("")
			ledger = JsonLedger.sync(hash_sum)
			self.stdout.write("......synced ledger %s" % ledger.id)
			while not options['onceonly'] and ledger and ledger.parent_hash and ledger.id % 1000000:
				self.stdout.write("...... syncing %s ... " % ledger.parent_hash, ending='')
				if JsonLedger.objects.filter(hash_sum=ledger.parent_hash):
					self.stderr.write("...!... got earlier synced ledger, quiting")
					break
				ledger = JsonLedger.sync(ledger.parent_hash)
				self.stdout.write("synced ledger %s" % ledger.id)
		elif options['websocket']:
			self.stdout.write("...sychronize using websocket")
			while True:
				try:
					socketIO = SocketIO("state.jingtum.com", 80, Namespace)
					self.stdout.write("...started websocket synchronization")
					socketIO.wait(3600)
				except Exception as e:
					self.stderr.write("...!... got exception using websocket")
					e
					time.sleep(20)
				time.sleep(10 * random.randint(1,10))
		elif options['missing']:
			self.stdout.write("...sychronize missing ledgers")
			ledger = JsonLedger.objects.order_by('-id').first()
			while True:
				while ledger.id > 9292000:
					try:
						ledger = JsonLedger.objects.get(id=ledger.id - 1)
					except Exception as e:
						self.stdout.write("...syncing missing ledger at %s" % (ledger.id - 1), ending='')
						ledger = JsonLedger.sync(ledger.parent_hash)
						self.stdout.write("...synced %s" % ledger.hash_sum)
				self.stdout.write("...sychronized missing ledgers")
				self.stdout.write("... next round of syncing soon...")
				time.sleep(60 * random.randint(15,30))
		else:
			self.stdout.write("...no arguments, try to continuing syching ledger")
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
					if JsonLedger.objects.filter(hash_sum=ledger.parent_hash):
						self.stderr.write("...!... got earlier synced ledger, quiting")
						break
					ledger = JsonLedger.sync(ledger.parent_hash)
					self.stdout.write("synced ledger %s" % ledger.id)
			else:
					self.stdout.print("finished")
		self.stdout.write(self.style.SUCCESS('Successfully sychronized ledgers'))
