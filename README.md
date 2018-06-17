Crowdsourcing (Django): Automatic profiling of skills in crowdsourcing systems
=====

The aim of the project is to create a crowdsourcing platform ([LiquidCrowd](https://www.sciencedirect.com/science/article/pii/S0167739X15001065)).

The system automatically provides a set of tasks to a cluster of users, comparing the different answers.
In this way it is possible to evaluate the consensus of the response, creating a user profile in order to provide
a task more suited to their figure. 


Campaign
----
The Campaign is a collection of Tasks to which a Worker can register.


Task
-----
The Task is a question automatically provided by the system to which a group of Workers answer.


Worker
----
The Worker is a user who subscribes to the platform and responds to tasks.
They are characterized by the measure of their trustworthiness and their score.
They can be promoted to Promoter to create Campaigns


Django Groups Configuration
----

![Django Groups](https://bytebucket.org/mangone/crowdsourcing-django/raw/17bd0edcbc8b19aface22f927ddaedbb14d65810/Django%20Groups.png)

