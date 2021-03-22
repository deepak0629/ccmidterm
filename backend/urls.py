"""midterm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import gethsnumdetails,loadcsv,login,signup,getspendvstime,getspendvstimedetailed,getmschart,getincomechart
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('gethsnumdetails/', gethsnumdetails),
    path('upload/',csrf_exempt(loadcsv)),
    path('login/',csrf_exempt(login)),
    path('signup/',csrf_exempt(signup)),
    path('getspendvstime/',csrf_exempt(getspendvstime)),
    path('getspendvstimedetailed/',csrf_exempt(getspendvstimedetailed)),
    path('getmschart/',csrf_exempt(getmschart)),
    path('getincomechart/',csrf_exempt(getincomechart))
]
