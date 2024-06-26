import logging

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import UsernameField
from django.core.mail import send_mail
from django.forms import inlineformset_factory
from . import models, widgets

logger = logging.getLogger(__name__)


class ContactForm(forms.Form):
    name = forms.CharField(label="Your Name", max_length=100)
    message = forms.CharField(max_length=600, widget=forms.Textarea)
    """
        Some of the most common fields in a Django form are as follows:
        • BooleanField: Typically a check box
        • CharField: A text input box (typically <input type="text"> or <textarea>)
        • ChoiceField: A selector between a set of options
        • DecimalField: A decimal
        • EmailField: A text input that uses a special widget to only accept e-mail addresses
        • FileField: A file input 44
        • ImageField: Like FileField, but only validates image formats
        • IntegerField: An integer
    """

    def send_mail(self):
        logger.info("Sending email to customer service")
        message = "From: {0}\n{1}".format(
            self.cleaned_data["name"],
            self.cleaned_data["message"],
        )

        send_mail(
            "Site message",
            message,
            "site@booktime.domain",
            ["customerservice@booktime.domain"],
            fail_silently=False,
        )


# Registration Page
class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = models.User
        fields = ("email",)
        field_classes = {"email": UsernameField}

    def send_mail(self):
        logger.info(
            "Sending signup email for email=%s",
            self.cleaned_data["email"],
        )
        message = "Welcome{}".format(self.cleaned_data["email"])
        send_mail(
            "Welcome to BookTime",
            message,
            "site@booktime.domain",
            [self.cleaned_data["email"]],
            fail_silently=True,
        )


class AuthenticationForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(strip=False, widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request

        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email is not None and password:
            self.user = authenticate(self.request, email=email, password=password)
        if self.user is None:
            raise forms.ValidationError("Invalid email/password combination.")
        logger.info("Authentication successful for email=%s", email)

        return self.cleaned_data

    def get_user(self):
        return self.user


"""
• formset_factory(): The simplest way, works best with normal forms
• modelformset_factory(): The equivalent of modelforms but applied to formsets
• inlineformset_factory(): Like the above but more specific for related objects (via foreign key) 
    to a base object
"""
BasketLineFormSet = inlineformset_factory(
    models.Basket,
    models.BasketLine,
    fields=("quantity",),
    extra=0,
    widgets={"quantity": widgets.PlusMinusNumberInput()},
)


# Checkout FLow
class AddressSelectionForm(forms.Form):
    billing_address = forms.ModelChoiceField(queryset=None)
    shipping_address = forms.ModelChoiceField(queryset=None)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = models.Address.objects.filter(user=user)
        self.fields["billing_address"].queryset = queryset
        self.fields["shipping_address"].queryset = queryset
