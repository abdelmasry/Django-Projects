from django import forms
from django.core.mail import send_mail
import logging

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
