from __future__ import unicode_literals
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal

class Worker(models.Model):
	id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
	genre = models.CharField(max_length=1)
	birth_date = models.DateField()
	w_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
	w_trustworthiness = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('1.00'))
	banned = models.BooleanField(default=False)

	def __unicode__(self):
		name = self.id.first_name + " " +self.id.last_name + " - " + self.id.username 
		return str(self.id.id) + ": " + name 

class Campaign(models.Model):
	name = models.TextField()
	creation_date = models.DateTimeField(default=timezone.now )
	start_date = models.DateField()
	finish_date = models.DateField()
	start_signup = models.DateField()
	finish_signup = models.DateField()
	init_trustworthiness = models.DecimalField(max_digits=4, decimal_places=2)
	w_campaign = models.ManyToManyField(Worker, through='Worker_Campaign')

	def __unicode__(self):
		return str(self.id) + ": " + self.name

class Task_Status(models.Model):
	name = models.TextField()

	def __unicode__(self):
		return str(self.id) + ": " + self.name
		
class Answer_Type(models.Model):
	name = models.TextField()

	def __unicode__(self):
		return str(self.id) + ": " + self.name

class Task(models.Model):
	description = models.TextField()
	answer_type = models.ForeignKey(Answer_Type, on_delete = models.CASCADE)
	insert_date = models.DateTimeField(default = timezone.now )
	priority = models.IntegerField(default = 0)
	final_answer = models.TextField(null = True, blank = True)
	campaign = models.ForeignKey(Campaign, on_delete = models.CASCADE)
	task_status = models.ForeignKey(Task_Status, on_delete = models.CASCADE)
	current_round = models.IntegerField(null = True,blank = True)
	w_task = models.ManyToManyField(Worker, through = 'Worker_Task')

	def __unicode__(self):
		return str(self.id) + ": Task - " + self.campaign.name

class Task_Setup(models.Model):
	num_worker = models.IntegerField()
	min_trustworthiness = models.DecimalField(max_digits=4, decimal_places=2)
	consensus_threshold = models.DecimalField(max_digits=4, decimal_places=2)
	max_exec_time = models.IntegerField()
	t_task_setup = models.ManyToManyField(Task, through='Task_Task_Setup')

class Worker_Campaign(models.Model):
	worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
	campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
	c_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
	c_trustworthiness = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('1.00'))
	worker_banned = models.BooleanField(default=False)

	def __unicode__(self):
		name = self.worker.id.first_name + " - " + self.campaign.name
		return name 

class Worker_Task(models.Model):
	id = models.AutoField(primary_key=True)
	worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
	task = models.ForeignKey(Task, on_delete=models.CASCADE)
	round = models.IntegerField()
	timeout = models.BooleanField(default=True)
	refused = models.BooleanField(default=False)
	timestamp_in = models.DateTimeField(default=timezone.now )
	timestamp_out = models.DateTimeField()
	answer = models.TextField(null=True,blank=True)
	current_w_trustworthiness = models.DecimalField(max_digits=4, decimal_places=2)

	def __unicode__(self):
		name = "Round " + str(self.round) + " - " + self.worker.id.username + " - Task: " + str(self.task.id)
		return name 

	class Meta:
	 unique_together = ('worker','task','round',)

class Task_Task_Setup(models.Model):
	task_setup = models.ForeignKey(Task_Setup, on_delete=models.CASCADE)
	task = models.ForeignKey(Task, on_delete=models.CASCADE)
	round = models.IntegerField()