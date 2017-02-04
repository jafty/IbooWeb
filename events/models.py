from django.db import models
from django.utils import timezone
from django.db.models import Q
from django.shortcuts import render
# Create your models here.
class Event(models.Model):
	author = models.ForeignKey('auth.User')
	title = models.CharField(max_length=50)
	price = models.DecimalField(max_digits=6, decimal_places=2)
	drink = models.BooleanField()
	date = models.DateTimeField()
	password_reg = models.CharField(max_length=50)
	password_acc = models.CharField(max_length=50)
	contact = models.TextField()
	description = models.TextField()
	stripe_user_id = models.CharField(max_length=140, default='SOME STRING')
	address = models.CharField(max_length=50)
	
	def __str__(self):
		return self.title

class UserProfile(models.Model):
	user = models.ForeignKey('auth.User')
	access_token = models.CharField(max_length=50)
	stripe_user_id = models.CharField(max_length=50)
	
	

	
		
	

		
		
		
	