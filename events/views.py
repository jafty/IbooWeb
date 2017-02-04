from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Event, UserProfile 
from django.contrib.auth.models import User
from .forms import PassForm, RegistrationForm, EventForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import urllib.request
import oauth2
import stripe
import json
import rauth
from rauth import OAuth2Service
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

stripe.api_key = "secret_key"

# Create your views here.
def index(request):
    return render(request, 'events/index.html')
	
@login_required
def event_list(request):
    events = Event.objects.all()
    return render(request, 'events/event_list.html', {'events':events})
   
@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'events/event_detail.html', {'event':event})

@login_required
def enter_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    form = PassForm(request.POST or None)
    if request.method == "POST":
        
        if form.is_valid():
            password = form.cleaned_data['password']
            if password == event.password_reg: 
                return render(request, 'events/charge.html', {'event':event})
            else:
                events = Event.objects.all()
                return render(request, 'events/event_list.html',{'events':events})

		
			
			
    return render(request, 'events/enter_event.html', {'form': form})

def register(request):
	if request.method == "POST":
		form = RegistrationForm(request.POST)
		if form.is_valid():
			user = User.objects.create_user(
			username=form.cleaned_data['username'],
			password=form.cleaned_data['password1'],
			email=form.cleaned_data['email']
			)
			events = Event.objects.all()
			return HttpResponseRedirect(reverse('index'))
	else:
		form = RegistrationForm()
	return render(request, 'events/register.html', {'form':form})

@login_required
def charge(request, pk):
	event = get_object_or_404(Event, pk=pk)
	stripe.api_key =  "secret_key" 
	token = request.POST['stripeToken']

	# Charge the user's card:
	charge = stripe.Charge.create(
		amount=599,
		currency="eur",
		description="Example charge",
		source=token,
		destination=event.stripe_user_id,
		application_fee=199,
		
	)


	return render(request, 'events/confirm.html', {'event':event})
	

@login_required
def connect_stripe(request):
	return render(request, 'events/connect_stripe.html')

@login_required	
def stripe_callback(request):
    stripe_connect_service = OAuth2Service(
        name = 'stripe',
        client_id = 'ca_A1MFPeV3GsQiotVP31CRHCv31jRmwkPZ',
        client_secret = 'secret_key',
        authorize_url = 'https://connect.stripe.com/oauth/authorize',
        access_token_url = 'https://connect.stripe.com/oauth/token',
        base_url = 'https://api.stripe.com/',
    )
	
    code = request.GET['code']
	
    data = {
        'grant_type': 'authorization_code',
        'code': code,
    }
    resp = stripe_connect_service.get_raw_access_token(method='POST', data=data)
    print(resp)
    
    stripe_payload = json.loads(resp.text)
    print(stripe_payload)
    stripe_user_id = stripe_payload["stripe_user_id"]
    access_token = stripe_payload["access_token"]
	
    #creer une classe profile 
    me = request.user
    UserProfile.objects.create(user=me, stripe_user_id=stripe_user_id, access_token=access_token)
    new_user=UserProfile.objects.get(user=me)
    return render(request, 'events/stripe_callback.html', {'new_user':new_user})
	
@login_required
def event_new(request):	
    me = request.user
    if UserProfile.objects.filter(user = me).exists():
    # at least one object satisfying query exists
    
        userProfileObject = UserProfile.objects.get(user=me)
        stripe_user_id = userProfileObject.stripe_user_id
        if request.method == "POST":
            form = EventForm(request.POST)
            if form.is_valid():
                event = form.save(commit=False)
                event.author = request.user
                event.stripe_user_id = stripe_user_id
                event.save()
                return HttpResponseRedirect(reverse('event_list'))
        else:
            form = EventForm()
        return render(request, 'events/event_new.html', {'form':form})
    
    return render(request, 'events/connect_stripe.html')
			

	


