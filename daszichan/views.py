import os
from chartit import DataPool, Chart
from moac.models import *
from django.shortcuts import render_to_response
from django.db.models import F, Sum, Avg, Count


def homepage(_):
	#NUM_LATEST = 5
	ds_ledger = DataPool(
		series=[
		{
			'options': { 
				'source': StatLedger.objects.order_by('date')
				#'source': OrgCount.objects.filter(date__gte=timezone.datetime(2017,11,1),org__name='ibmcom')
			},
			'terms': [
				{'date': 'date'},
				{'Daily Max of Txs': 'ledger_txs__num_txs'}
			]
		},
		{
			'options': {
				'source': StatLedger.objects.order_by('date')
			},
			'terms': [
				{'date': 'date'},
				{'Daily Max of Tps': 'ledger_tps__tps'}
			]
		},
		]
	)


	cht_ledger = Chart(
		datasource=ds_ledger,
		series_options=[
		{
			'options': {
				'type': 'line',
				'stacking': False,
				'yAxis': 0,
			},
			'terms': {
				'date': [
					'Daily Max of Txs',
					],
			}
		},
		{
			'options': {
				'type': 'line',
				'stacking': False,
				'yAxis': 1,
			},
			'terms': {
				'date': [
					'Daily Max of Tps',
					],
			}
		},
		],

		chart_options={
			'title': {
				'text': 'daily block statistic: max TXS (left y) and max TPS(right y)'
			},
			'xAxis':
				{
				'type': 'date',
				'tickInterval': 1,
				'title': {
					'text': ' '
					}
				},
			'yAxis': [
				{
				'title': {
					'text': 'Number Of Transactions',
				},
				'min': 0
				},
				{
				'title': {
					'text': 'Transactions Per Second',
				},
				'min': 0,
				'opposite': True
				},
			],
			'chart': {
				'zoomType': 'x',
			},
			},
		)

	return render_to_response('index.html', {'chart_list': [ cht_ledger ], 'Addresses': Address.objects.count(), 'Ledgers': Ledger.objects.count(), 'Transactions': Transaction.objects.count(), 'Uncles': Uncle.objects.count(), 'difficulty_in_tera': int(Ledger.objects.last().difficulty // 1e12), 'uncle_ratio': int(Uncle.objects.count() * 100 / Ledger.objects.count()), 'MoacMined': 2 * (Ledger.objects.count() + Uncle.objects.count()), 'QueryableMoac': int(Address.objects.aggregate(Sum('balance'))['balance__sum'])})

