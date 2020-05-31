from django.contrib import admin
from django.urls import path
from .views import RemindMeApiView

urlpatterns = [
    path('', RemindMeApiView.as_view(), name ='reminder'),
]
