from django.contrib import admin
from .models import *
from decimal import Decimal

# Register your models here.
@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
	list_display = ('name','issuer')

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
	list_display = ('name','wallet','user')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
	list_display = ('amount','direction','currency','date','counterparty','memos')
	list_filter = ('deposite','withdraw','direction','agent','activation')
	#list_filter = ('deposite','withdraw','direction','counterparty__agent')
	#list_filter = ('deposite','withdraw','currency',)
	date_hierarchy = 'date'
	actions = ['summarize_amount']

	def summarize_amount(self,request,queryset):
		total = Decimal(0)
		for obj in queryset:
			total  += obj.amount
		self.message_user(request,"total amount: %s" % total)

	summarize_amount.short_description = "calculate sum of selected transactions amounts"

