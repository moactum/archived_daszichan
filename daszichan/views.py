from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect

class AgentForm(forms.Form):
	agent_no = forms.IntegerField(label="代理编号", initial=00)
	wallet   = forms.CharField(label="钱包地址", max_length=60)

def homepage(request):
	if request.method == 'POST':
		form = AgentForm(request.POST)
		if form.is_valid():
			return HttpResponseRedirect('/agents')
	else:
		form = AgentForm()
		return render(request, "homepage.html", { 'form': form } )
