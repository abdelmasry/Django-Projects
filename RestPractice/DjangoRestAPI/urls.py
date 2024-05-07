from . import views
from django.urls import path  
  
urlpatterns = [  
    path('basic/', views.StudentView.as_view())  
]  