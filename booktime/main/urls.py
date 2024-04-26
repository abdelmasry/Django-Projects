from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from . import views

from . import models

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name="signup"),
    path(
        "product/<slug:slug>/",
        DetailView.as_view(model=models.Product),
        name="product",
    ),

    path("about-us/", TemplateView.as_view(template_name="about_us.html")),
    path("", TemplateView.as_view(template_name="home.html")),
]
