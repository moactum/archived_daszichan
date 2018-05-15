from django.contrib import admin
from jsonstore.models import *
from moac.models import *
from django.contrib.admin.actions import delete_selected
from decimal import Decimal
import csv
from django.http import HttpResponse

# Register your models here.
class JsonMoacLedgerAdmin(admin.ModelAdmin):
	list_display = ('id','data')
	def has_change_permission(self,request,obj=None):
		if obj:
			return False
		return True
	def has_module_permission(self,request):
		return True

	
class LedgerAdmin(admin.ModelAdmin):
	list_display = ('number','timestamp','miner','hash')

	def has_change_permission(self,request,obj=None):
		if obj:
			return False
		return True
		#return request.user.is_anonymous
	def has_module_permission(self,request):
		return True

class TransactionAdmin(admin.ModelAdmin):
	list_display = ('ledger','hash')

	def has_change_permission(self,request,obj=None):
		if obj:
			return False
		return True
	def has_module_permission(self,request):
		return True

class AdminSite(admin.sites.AdminSite):
	site_header = 'public'
	site_title  = 'public'
	index_title = 'public'

	def has_permission(self,request):
		return True

my_admin_site_public = AdminSite(name='public')
my_admin_site_public.disable_action('delete_selected')
my_admin_site_public.register(Ledger,LedgerAdmin)
my_admin_site_public.register(Transaction,TransactionAdmin)
#my_admin_site_public.register(JsonMoacLedger,JsonMoacLedgerAdmin)
