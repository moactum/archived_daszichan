import os
from chartit import DataPool, Chart
from .models import MonthlyWeatherByCity
from .decorators import add_source_code_and_doc
from django.shortcuts import render_to_response
from icp.models import *
from django.db.models import F, Sum, Avg, Count


def homepage(_):
	NUM_LATEST = 10
	latest_stats = list()
	latest_stats.append(['Total to Date (all versions of CfC & ICP)', OrgCount.objects.filter(org__name='ibmcom').last().count])
	latest_stats.append(['Total since Nov 1, 2017', OrgCount.objects.filter(org__name='ibmcom').last().count - OrgCount.objects.filter(org__name='ibmcom',date__lte=timezone.datetime(2017,11,1)).last().count])
	latest_stats.append(['Average downloads per day (7 days a week)', OrgCount.objects.filter(org__name='ibmcom').last().count_per_day_avg])
	latest_dates = RepoCount.objects.filter(target__name='cfc-installer').reverse().dates('date','day')[:NUM_LATEST:1]
	latest_dates.reverse()
	latest_pulls = dict()
	for target in Repository.objects.filter(org__isnull=False):
		latest_pulls[target] = []
		for date in latest_dates:
			try:
				count = RepoCount.objects.get(target=target,date=date)
				latest_pulls[target].append(count.count)
			except RepoCount.DoesNotExist:
				latest_pulls[target].append(0)
	ds = DataPool(
		series=[
		{
			'options': { 
				'source': ArchCount.objects.filter(date__gte=timezone.datetime(2017,1,1),arch__name='power')
				#'source': ArchCount.objects.filter(arch__name='power').filter(date__gte=timezone.datetime(2017,11,1))
			},
			'terms': [
				{'power-date': 'date'},
				{'dockerhub pulls power': 'count'}
			]
		},
		{
			'options': {
				'source': ArchCount.objects.filter(date__gte=timezone.datetime(2017,1,1),arch__name='x86')
				#'source': ArchCount.objects.filter(arch__name='x86').filter(date__gte=timezone.datetime(2017,11,1))
			},
			'terms': [
				{'x86-date': 'date'},
				{'dockerhub pulls x86': 'count'}
			]
		},
		]
	)

	ds_version = DataPool(
		series=[
		{
			'options': {
				'source': VerCount.objects.filter(date__gte=timezone.datetime(2017,1,1),ver__name='icp')
				#'source': ArchCount.objects.filter(arch__name='x86').filter(date__gte=timezone.datetime(2017,11,1))
			},
			'terms': [
				{'icp-date': 'date'},
				{'post 2.1 pulls': 'count_per_day_avg'}
			]
		},
		{
			'options': { 
				'source': VerCount.objects.filter(date__gte=timezone.datetime(2017,1,1),ver__name='cfc')
				#'source': ArchCount.objects.filter(arch__name='power').filter(date__gte=timezone.datetime(2017,11,1))
			},
			'terms': [
				{'cfc-date': 'date'},
				{'pre 2.1 pulls': 'count_per_day_avg'}
			]
		},
		]
	)

	ds_compare = DataPool(
		series=[
		{
			'options': { 
				'source': OrgCount.objects.filter(date__gte=timezone.datetime(2017,1,1),org__name='ibmcom')
				#'source': OrgCount.objects.filter(date__gte=timezone.datetime(2017,11,1),org__name='ibmcom')
			},
			'terms': [
				{'ibm-date': 'date'},
				{'IBM Cloud Private pulls': 'count'}
			]
		},
		{
			'options': {
				'source': OrgCount.objects.filter(date__gte=timezone.datetime(2017,1,1),org__name='openshift')
			},
			'terms': [
				{'openshift-date': 'date'},
				{'OpenShift pulls': 'count'}
			]
		},
		]
	)

	ds_installs = DataPool(
		series=[
		{
			'options': { 
				'source': OrgCount.objects.filter(date__gte=timezone.datetime(2017,1,1),org__name='ibmcom')
				#'source': ArchCount.objects.filter(arch__name='power').filter(date__gte=timezone.datetime(2017,11,1))
			},
			'terms': [
				{'date': 'date'},
				{'Daily Total Installs': 'count_per_day'},
				{'7-Day Running Average': 'count_per_day_avg'},
			]
		},
		]
	)

	ds_power = DataPool(
		series=[
		{
			'options': { 
				'source': ArchCount.objects.filter(date__gte=timezone.datetime(2017,1,1),arch__name='power').annotate(ratio=F('count_per_day_avg') * 100 /F('count_per_day_all_avg'))
				#'source': ArchCount.objects.filter(arch__name='power').filter(date__gte=timezone.datetime(2017,11,1))
			},
			'terms': [
				{'date': 'date'},
				{'7-Day Running Average %': 'ratio'}
			]
		},
		]
	)
	def monthname(month_num):
		names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
				 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
		return names[month_num]

	cht = Chart(
		datasource=ds,
		series_options=[{
			'options': {
				'type': 'area',
				'stacking': True
			},
			'terms': {
				'power-date': [
					'dockerhub pulls power',
					],
				'x86-date': [
					'dockerhub pulls x86',
					],
			}
		}],
		chart_options={
			'title': {
				'text': 'Cumulative Installs (dockerhub pulls of installer images)'
			},
			'xAxis': {
				'type': 'date',
				'tickInterval': 15,
				'title': {
					'text': ' '
				}
			},
			'yAxis': {
				'title': {
					'text': 'installs (dockerhub pulls)'}
			},
			'chart': {
				'zoomType': 'x',
			},
			},
		)

	cht_version = Chart(
		datasource=ds_version,
		series_options=[{
			'options': {
				'type': 'area',
				'stacking': True
			},
			'terms': {
				'icp-date': [
					'post 2.1 pulls',
					],
				'cfc-date': [
					'pre 2.1 pulls',
					],
			}
		}],
		chart_options={
			'title': {
				'text': 'Pre vs Post 2.1B1 Installs/Day (7-Day Running Averages)'
			},
			'xAxis': {
				'type': 'date',
				'tickInterval': 15,
				'title': {
					'text': ' '
				}
			},
			'yAxis': {
				'title': {
					'text': ' '}
			},
			'chart': {
				'zoomType': 'x',
			},
			},
		)

	cht_compare = Chart(
		datasource=ds_compare,
		series_options=[
		{
			'options': {
				'type': 'line',
				'stacking': False,
				'yAxis': 0,
			},
			'terms': {
				'openshift-date': [
					'OpenShift pulls',
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
				'ibm-date': [
					'IBM Cloud Private pulls',
					],
			}
		},
		],

		chart_options={
			'title': {
				'text': 'Installs: ICP vs OpenShift (cumulative)'
			},
			'xAxis':
				{
				'type': 'date',
				'tickInterval': 15,
				'title': {
					'text': ' '
					}
				},
			'yAxis': [
				{
				'title': {
					'text': 'openshift installs',
				},
				'min': 0
				},
				{
				'title': {
					'text': 'icp installs',
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

	cht_installs = Chart(
		datasource=ds_installs,
		series_options=[{
			'options': {
				'type': 'line',
				'stacking': False
			},
			'terms': {
				'date': [
					'Daily Total Installs',
					'7-Day Running Average',
					],
			}
		}],
		chart_options={
			'title': {
				'text': 'Installs Per Day'
			},
			'xAxis': {
				'type': 'date',
				'tickInterval': 15,
				'title': {
					'text': ' '
				}
			},
			'yAxis': {
				'title': {
					'text': ' '}
			},
			'chart': {
				'zoomType': 'x',
			},
			},
		)

	cht_power = Chart(
		datasource=ds_power,
		series_options=[{
			'options': {
				'type': 'line',
				'stacking': False
			},
			'terms': {
				'date': [
					'7-Day Running Average %',
					],
			}
		}],
		chart_options={
			'tooltip': {
				'enabled': False
			},
			'title': {
				'text': 'Power Installs as Percentage of All'
			},
			'xAxis': {
				'type': 'date',
				'tickInterval': 15,
				'title': {
					'text': ' '
				}
			},
			'yAxis': {
				'title': {
					'text': ' '
				},
				'labels': {
					'format': '{value}%'
				},
			},
			'chart': {
				'zoomType': 'x',
			},
			},
		)
	return render_to_response('index.html', {'chart_list': [cht, cht_installs, cht_power, cht_compare, cht_version], 'latest_dates': latest_dates, 'latest_pulls': latest_pulls, 'latest_stats': latest_stats})


@add_source_code_and_doc
def demohome(_, title, code, doc, sidebar_items):
	"""
	Welcome to the Django-Chartit Demo. This demo has a lot of sample charts
	along with the code to help you get familiarized with the Chartit API.

	The examples start with simple ones and get more and  more complicated.
	The latter examples use concepts explained in the examples earlier. So if
	the source code of a particular chart looks confusing, check to see if any
	details have already been explained in a previous example.

	The models that the examples are based on are explained in Model Details.

	Thank you and have fun exploring!
	"""
	code = None
	return render_to_response('demohome.html',
							  {'chart_list': None,
							   'code': code,
							   'title': title,
							   'doc': doc,
							   'sidebar_items': sidebar_items})


@add_source_code_and_doc
def model_details(_, title, code, doc, sidebar_items):
	"""
	All the charts in this section are based on the following Models.
	Model data is available as migrations, found inside charit git
	repository.
	"""
	fname = os.path.join(os.path.split(os.path.abspath(__file__))[0],
						 'models.py')
	with open(fname) as f:
		code = ''.join(f.readlines())
	return render_to_response('model_details.html',
							  {'code': code,
							   'title': title,
							   'doc': doc,
							   'sidebar_items': sidebar_items})
