from django.urls import path

from . import views

urlpatterns = [
    path('',views.home,name='home'),   #  '/' or ' ' is referred as home
    path('optimize',views.optimize,name='optimize'),
    #path('results',views.results,name='results'),
    path('download',views.download,name='download'),
    path('repeat',views.home,name='repeat'),
    path('hadfile',views.hadfile,name='hadfile'),
    path('apply',views.apply,name='apply'),
    path('view_all',views.view_all,name='view_al'),

]
