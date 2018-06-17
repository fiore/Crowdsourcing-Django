from __future__ import unicode_literals
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, models
from django.contrib.auth.models import User as UserModel, Group
from django.views.generic import View
from .models import Worker, Worker_Campaign, Task_Status, Answer_Type, Task_Setup
from .models import Campaign as CampaignModel, Task as TaskModel, Worker_Task as Worker_TaskModel, Task_Task_Setup

from .forms import UserForm, LoginForm, UploadFileForm
from datetime import datetime
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from collections import Counter

import json, string, random

class IndexView(generic.ListView):
	template_name = 'crowdsourcing/index.html'
	context_object_name = 'all_workers'

	def get_queryset(self):
		group = models.Group.objects.get(name='Workers')		
		return group.user_set.all()

	def get_context_data(self, **kwargs):

		context = super(IndexView, self).get_context_data(**kwargs)
		
		userLogged = self.request.user

		if userLogged.is_authenticated():

			if userLogged.groups.filter(name__in=['Workers']).exists():

				worker = Worker.objects.get(id=userLogged)
				campaignSignedUp = Worker_Campaign.objects.filter(worker=worker, worker_banned=False)
				campaignSignedUpID = campaignSignedUp.values('campaign_id')

				context['already_joined'] = CampaignModel.objects.filter(id__in=campaignSignedUpID)

				context['to_join'] = CampaignModel.objects.exclude(id__in=campaignSignedUpID).exclude(finish_signup__lte=datetime.now().date())

				context['score_trust'] = campaignSignedUp

		return context

class CaratteristicheView(View):
	template_name = 'crowdsourcing/caratteristiche.html'

	def get(self, request):
		return render(request, self.template_name)

class FunzionamentoView(View):
	template_name = 'crowdsourcing/funzionamento.html'

	def get(self, request):
		return render(request, self.template_name)

class Register(View):
	form_class = UserForm
	template_name = 'crowdsourcing/register.html'

	def get(self, request):
		if request.user.is_authenticated:
			return redirect('crowdsourcing:index')

		form = self.form_class(None)
		return render(request, self.template_name, {'form' : form})

	def post(self, request):
		if request.user.is_authenticated:
			return redirect('crowdsourcing:index')

		form = UserForm(request.POST)

		if form.is_valid():

			user = form.save(commit=False)
			
			first_name = form.cleaned_data['first_name']
			last_name = form.cleaned_data['last_name']
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			email = form.cleaned_data['email']
			
			if UserModel.objects.filter(email=email).exists():
				return render(request, self.template_name,
					{'form' : form, 'email' : 'A user with that email already exists.'} )

			user.set_password(user.password)
			form.save()

			g = Group.objects.get(name='Workers') 
			g.user_set.add(user)

			worker = Worker(id=user, genre=request.POST['genre'], birth_date=request.POST['birth_date'])
			worker.save()
			
			if user is not None:
				return redirect('crowdsourcing:index')

		return render(request, self.template_name, {'form' : form})

class Login(View):
	form_class = LoginForm
	template_name = 'crowdsourcing/header.html'
	
	def get(self, request):
		form = self.form_class(None)
		return redirect('crowdsourcing:index')

	def post(self, request):
		form = self.form_class(request.POST)

		username = request.POST['username']
		password = request.POST['password']
		try:
			user = UserModel.objects.get(username=username)
			if not(user.is_superuser):
				Worker.objects.get(id=user, banned=False)
		except ObjectDoesNotExist:
			messages.error(request, 'User does not exist or they were banned')
			return HttpResponseRedirect(reverse('crowdsourcing:index'))
		
		user = authenticate(username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect('crowdsourcing:index')
		else:
			messages.error(request, "Your password didn't match. Please try again")
			return HttpResponseRedirect(reverse('crowdsourcing:index'))

def Logout(request):
	logout(request)
	return redirect('crowdsourcing:index')

class User(View):
	template_name = 'crowdsourcing/user.html'

	def get(self, request):
		if request.user.is_authenticated:
			userLogged = self.request.user
			worker = Worker.objects.get(id=userLogged)

			userInfo = {
				'username': userLogged.username,
				'first_name': userLogged.first_name,
				'last_name': userLogged.last_name,
				'email': userLogged.email,
				'groups': userLogged.groups.all()[0].name,
				'date_joined': userLogged.date_joined,
				'w_score': worker.w_score,
				'w_trustworthiness': worker.w_trustworthiness
			}

			return render(request, self.template_name, {'userInfo' : userInfo})

		return redirect('crowdsourcing:index')	
	
	def post(self, request):

		if request.user.is_authenticated:
			userLogged = self.request.user
			worker = Worker.objects.get(id=userLogged)

			userInfo = {
				'username': userLogged.username,
				'first_name': userLogged.first_name,
				'last_name': userLogged.last_name,
				'email': userLogged.email,
				'groups': userLogged.groups.all()[0].name,
				'date_joined': userLogged.date_joined,
				'w_score': worker.w_score,
				'w_trustworthiness': worker.w_trustworthiness
			}
	
			old_psw = request.POST['old_psw']
			new_psw = request.POST['new_psw']

			if userLogged.check_password(old_psw):
				u = UserModel.objects.get(username=userLogged.username)
				u.set_password(new_psw)
				u.save()
				return render(request, self.template_name,{'userInfo' : userInfo, 'psw_message' : 'Password changed successfully'} )
			return render(request, self.template_name,{'userInfo' : userInfo, 'psw_message' : 'Password incorrect'} )

class Promote(View):

	def get(self, request):
		return redirect('crowdsourcing:index')

	def post(self, request):
		if request.POST:
		
			for worker in request.POST.getlist('worker_list'):
				user = UserModel.objects.get(username=worker)
				p = Group.objects.get(name='Promoters')
				w = Group.objects.get(name='Workers')
				p.user_set.add(user)
				w.user_set.remove(user)

		return redirect('crowdsourcing:index')

class Campaign(View):
	form_class = UploadFileForm
	template_name = 'crowdsourcing/campaign.html'	

	def get(self, request):

		userLogged = self.request.user
		
		if userLogged.is_authenticated:
			if userLogged.groups.filter(name__in=['Workers']).exists():
				return redirect('crowdsourcing:index')

			form = self.form_class(None)
			return render(request, self.template_name, {'form' : form})

		return redirect('crowdsourcing:index')

	def post(self, request):
		fileName = settings.MEDIA_ROOT+'/tasks_' + self.request.user.username + '.json'

		def handle_uploaded_file(f):
			with open(fileName, 'wb+') as destination:
				for chunk in f.chunks():
					destination.write(chunk)

		form = UploadFileForm(request.POST, request.FILES)
		
		if form.is_valid():

			campaign = CampaignModel(name = request.POST['name'], start_date = request.POST['start_date'],
				finish_date = request.POST['finish_date'], start_signup = request.POST['start_signup'],
				finish_signup = request.POST['finish_signup'], init_trustworthiness = request.POST['init_trustworthiness'])

			campaign.save()

			handle_uploaded_file(request.FILES['file'])
			json_data = open(fileName)
			data = json.load(json_data)

			answer_type = Answer_Type.objects.get(name='loaded')
			task_status = Task_Status.objects.get(id=1)

			for item in data["tasks"]:
				description = json.dumps(item, ensure_ascii=False)
				description = description.replace('\\x', '\\u00')
				task = TaskModel(description = description, answer_type = answer_type, priority = settings.TASK_PRIORITY, campaign = campaign,
					task_status = task_status)
				task.save()

			json_data.close()

			return redirect('crowdsourcing:index')
		
		return render(request, self.template_name, {'form' : form})

class SignUpToCampaign(View):

	def get(self, request, campaign_id):
		return redirect('crowdsourcing:index')

	def post(self, request, campaign_id):
		if request.POST:
		
			SUtoCampaign = CampaignModel.objects.get(id=campaign_id)
			worker = Worker.objects.get(id=self.request.user)
			wc = Worker_Campaign(worker=worker, campaign=SUtoCampaign)
			wc.save()

		return redirect('crowdsourcing:index')

class Task(View):
	template_name = 'crowdsourcing/task.html'

	def get(self, request):
		return HttpResponseRedirect(reverse('crowdsourcing:index'))

	def post(self, request):

		if request.user.is_authenticated:
			
			userLogged = self.request.user
			worker = Worker.objects.get(id=userLogged)

			if request.POST['answer'] == 'false':
				campaign = CampaignModel.objects.get(id=request.POST['campaign'])

				campaignTasksList = TaskModel.objects.filter(campaign = request.POST['campaign']).values_list('id', flat=True)
				campaignTasksList = list(campaignTasksList)

				while True:

					if not campaignTasksList :
						messages.warning(request, 'No Task avaible for Campaign: ' + campaign.name)
						return HttpResponseRedirect(reverse('crowdsourcing:index'))

					else :
						idRandom = random.choice(campaignTasksList)

						task = TaskModel.objects.get(id=idRandom)

						task_status = Task_Status.objects.get(name='loaded')
						task_setup = Task_Setup.objects.get(id=1)
						tts = Task_Task_Setup.objects.get(task_setup = task_setup, task = task)
								
						if task.current_round is None :
							task.current_round = 1
							task.save()

						if task.task_status == task_status and task.current_round <= tts.round :

							count = Worker_TaskModel.objects.filter(task = task, round = task.current_round).count()

							if count < task_setup.num_worker and worker.w_trustworthiness > task_setup.min_trustworthiness :

								try:
									Worker_TaskModel.objects.get(worker=worker,task=task,round=task.current_round)

									campaignTasksList.remove(idRandom)
								
								except ObjectDoesNotExist:
									break

							else :
								campaignTasksList.remove(idRandom)

						else :
							campaignTasksList.remove(idRandom)

				decoded_json = json.loads(task.description)
				context = decoded_json['context']
				title = decoded_json['title']
				title = string.replace(title, '\n', '<br>')
				choices = decoded_json['choices']

				dict = {
					'countdown': task_setup.max_exec_time,
					'task': idRandom,
					'round': task.current_round,
					'context': context,
					'title': title,
					'choices': choices
				}

				worker_task = Worker_TaskModel(
					worker = worker,
					task = task,
					round = task.current_round,
					timestamp_out = datetime.now().date(),
					answer = '',
					current_w_trustworthiness = worker.w_trustworthiness
				)

				worker_task.save()

				return render(request, self.template_name, dict)

			elif request.POST['answer'] == 'true' :
				wt = Worker_TaskModel.objects.filter(worker=worker, task=request.POST['task'], round=request.POST['round'])
				
				if 'choices' in request.POST:
					wt.update(timeout = False, answer = request.POST['choices'],timestamp_out = datetime.now())
					
					list_answer = Worker_TaskModel.objects.filter(task = request.POST['task'], round = request.POST['round']).exclude(answer__isnull=True).exclude(answer__exact='')
					count = list_answer.count()
					task_setup = Task_Setup.objects.get(id=1)

					if count == task_setup.num_worker :

						task = TaskModel.objects.get(id=request.POST['task'])
						task_setup = Task_Setup.objects.get(id=1)
						tts = Task_Task_Setup.objects.get(task_setup = task_setup, task = task)

						CATrust = 0

						totalTrust = 0

						
						# q-constraint :

						for x in list_answer.values('answer', 'current_w_trustworthiness') :
							w_trust = float(x.get('current_w_trustworthiness'))

							totalTrust += w_trust

						counter = Counter(list(list_answer.values_list('answer', flat=True)))

						CA1 = counter.most_common(1).pop()[0]

						Trust_threshold = totalTrust * float(task_setup.consensus_threshold)

						maxTrust_CA1 = 0

						for x in list_answer.values('answer', 'current_w_trustworthiness') :

							if int(x.get('answer')) == int(CA1):
								worker_trust = float(x.get('current_w_trustworthiness'))
								CATrust += worker_trust
								maxTrust_CA1 = worker_trust if worker_trust > maxTrust_CA1 else maxTrust_CA1

						if CATrust > Trust_threshold :

							print "q-constraint verificato"

							# bop-constraint :

							CA2 = counter.most_common(2).pop()[0]

							for x in list_answer.values('answer', 'current_w_trustworthiness') :

								if int(x.get('answer')) == int(CA2):
									worker_trust = float(x.get('current_w_trustworthiness'))
									CATrust += worker_trust

							if CATrust + maxTrust_CA1 < Trust_threshold :

								print "bop-constraint verificato"

								task.final_answer = CA1
								answer_type = Answer_Type.objects.get(name = 'terminated')
								task.answer_type = answer_type
								task.save()

							else : 

								print "bop-constraint non verificato"								

								if task.current_round < tts.round :
									task.current_round += 1
									task.save()

								else : 
									answer_type = Answer_Type.objects.get(name = 'terminated')
									task.answer_type = answer_type
									task.save()

						else :
							print "q-constraint non verificato"

							if task.current_round < tts.round :
								task.current_round += 1
								task.save()

							else : 
								answer_type = Answer_Type.objects.get(name = 'terminated')
								task.answer_type = answer_type
								task.save()

				else:
					wt.update(timeout=False, refused=True, timestamp_out=datetime.now())
			elif request.POST['answer'] == 'none' :
					wt.update(timestamp_out=datetime.now())

					
		return HttpResponseRedirect(reverse('crowdsourcing:index'))