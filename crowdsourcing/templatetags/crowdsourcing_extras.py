from django import template
from django.contrib.auth.models import Group
from datetime import date, datetime, timedelta

register = template.Library() 

@register.filter(name='has_group') 
def has_group(user, group_name):
	group =  Group.objects.get(name=group_name) 
	return group in user.groups.all()

@register.filter() 
def to_space(value):
	return value.replace("_"," ")

@register.filter(expects_localtime=True)
def is_past(value):
	return value < date.today()

@register.filter(expects_localtime=True)
def is_future(value):
	return value > date.today()