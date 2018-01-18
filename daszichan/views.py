from django.shortcuts import render
from django import forms
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from jingtum.models import Agent, Wallet

class AgentForm(forms.Form):
	wallet   = forms.CharField(label="钱包地址", max_length=60)

@login_required
def homepage(request):
	if not request.user.agent:
		agent,created = Agent.objects.get_or_create(name=request.user.username,user=request.user)
	else:
		agent = request.user.agent
	if request.method == 'POST':
		form = AgentForm(request.POST)
		if form.is_valid():
			try:
				address = form.cleaned_data['wallet']
				if not agent.wallet or agent.wallet.address != address:
					agent.wallet = Wallet.objects.get(address=address)
					agent.save()
				print("handle post")
				return HttpResponseRedirect('/agents/')
			except Exception as e:
				print(e)
				pass
		return HttpResponseRedirect('/')
	else:
		form = AgentForm()
		if agent.wallet:
			return HttpResponseRedirect('/agents/')
		return render(request, "homepage.html", { 'form': form } )
