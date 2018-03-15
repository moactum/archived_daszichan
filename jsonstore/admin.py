from django.contrib import admin

# Register your models here.
from jsonstore.models import *

@admin.register(JsonLedger)
class JsonLedgerAdmin(admin.ModelAdmin):
	list_display = ('id', 'hash_sum')
