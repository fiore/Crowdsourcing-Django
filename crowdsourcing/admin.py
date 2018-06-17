# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Worker)
admin.site.register(Campaign)
admin.site.register(Task_Status)
admin.site.register(Answer_Type)
admin.site.register(Task)
admin.site.register(Task_Setup)
admin.site.register(Worker_Campaign)
admin.site.register(Worker_Task)
admin.site.register(Task_Task_Setup)