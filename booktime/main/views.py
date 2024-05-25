import logging

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic.edit import FormView, CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django import forms as django_forms
from django.db import models as django_models
import django_filters
from django_filters.views import FilterView

from . import forms, models

logger = logging.getLogger(__name__)


# Create your views here.


class ProductListView(ListView):
    template_name = "main/product_list.html"
    paginate_by = 4

    def get_queryset(self):
        tag = self.kwargs["tag"]
        self.tag = None

        if tag != "all":
            self.tag = get_object_or_404(models.ProductTag, slug=tag)
        if self.tag:
            products = models.Product.objects.active().filter(tags=self.tag)
        else:
            products = models.Product.objects.active()

        return products.order_by("name")


class ContactUsView(FormView):
    template_name = "contact_us.html"
    form_class = forms.ContactForm
    success_url = "/"

    def form_valid(self, form):
        form.send_mail()
        return super().form_valid(form)


# Registration Page
class SignupView(FormView):
    template_name = "signup.html"
    form_class = (
        forms.UserCreationForm
    )  # ModelForm pattern: a form that manages loading, validation, and saving

    def get_success_url(self):
        redirect_to = self.request.GET.get("next", "/")
        return redirect_to

    def form_valid(self, form):
        response = super().form_valid(form)
        form.save()
        email = form.cleaned_data.get("email")
        raw_password = form.cleaned_data.get("password1")
        logger.info("New signup for email=%s through SignupView", email)
        user = authenticate(email=email, password=raw_password)
        login(self.request, user)
        form.send_mail()
        messages.info(self.request, "You signed up successfully.")

        return response


class AddressListView(LoginRequiredMixin, ListView):
    model = models.Address

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class AddressCreateView(LoginRequiredMixin, CreateView):
    """
    In your case, since you're using
    a CreateView with the Address model,
    Django will look for a template named address_form.html
    by default. This is part of Django's convention
    over configuration principle,
    where it tries to infer the template name based
    on the model name and the type of view being used.
    """

    model = models.Address
    fields = [
        "name",
        "address1",
        "address2",
        "zip_code",
        "city",
        "country",
    ]
    success_url = reverse_lazy("address_list")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return super().form_valid(form)


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Address
    fields = [
        "name",
        "address1",
        "address2",
        "zip_code",
        "city",
        "country",
    ]
    success_url = reverse_lazy("address_list")

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Address
    success_url = reverse_lazy("address_list")

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


def add_to_basket(request):
    """
    In this view we can rely on the middleware to position
    the existing basket inside the request.basket attribute.
    This will only work if the basket exists, and its id is in the session already.
    This view will also take care of creating a basket if it does not exist yet,
    and do the necessary steps for the middleware to work for any following request.

    """
    product = get_object_or_404(models.Product, pk=request.GET.get("product_id"))
    basket = request.basket
    if not request.basket:
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None
        basket = models.Basket.objects.create(user=user)
        request.session["basket_id"] = basket.id
    basketline, created = models.BasketLine.objects.get_or_create(
        basket=basket, product=product
    )
    if not created:
        basketline.quantity += 1
        basketline.save()
    return HttpResponseRedirect(reverse("product", args=(product.slug,)))


def manage_basket(request):
    if not request.basket:
        return render(request, "basket.html", {"formset": None})
    if request.method == "POST":
        formset = forms.BasketLineFormSet(request.POST, instance=request.basket)
        if formset.is_valid():
            formset.save()
    else:
        formset = forms.BasketLineFormSet(instance=request.basket)
    if request.basket.is_empty():
        return render(request, "basket.html", {"formset": None})

    return render(request, "basket.html", {"formset": formset})


class AddressSelectionView(LoginRequiredMixin, FormView):
    template_name = "address_select.html"
    form_class = forms.AddressSelectionForm
    success_url = reverse_lazy("checkout_done")

    def get_form_kwargs(self):
        """extracts the user from the request and returns it in a dictionary"""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        """
        Delete the basket from the session
        Call the create_order() method on it, with the submitted addresses data.
        """

        del self.request.session["basket_id"]
        basket = self.request.basket
        basket.create_order(
            form.cleaned_data["billing_address"], form.cleaned_data["shipping_address"]
        )
        return super().form_valid(form)


class DateInput(django_forms.DateInput):
    input_type = "date"


class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = models.Order

        fields = {
            "user__email": ["icontains"],
            "status": ["exact"],
            "date_updated": ["gt", "lt"],
            "date_added": ["gt", "lt"],
        }
        filter_overrides = {
            django_models.DateTimeField: {
                "filter_class": django_filters.DateFilter,
                "extra": lambda f: {"widget": DateInput},
            }
        }


class OrderView(UserPassesTestMixin, FilterView):
    """
    OrderView is a view that is only available to users that have access to the admin interface as well,
    as the test_func function checks for that. This view inherits from FilterView,
    with a filterset_class that specifies what filters are available in the page.

    Args:
        UserPassesTestMixin (_type_): _description_
        FilterView (_type_): _description_

    Returns:
        _type_: _description_
    """

    filterset_class = OrderFilter
    login_url = reverse_lazy("login")

    def test_func(self):
        return self.request.user.is_staff is True
