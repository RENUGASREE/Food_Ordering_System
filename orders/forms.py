from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class AddToCartForm(forms.Form):
    item_id = forms.CharField(widget=forms.HiddenInput())
    qty = forms.IntegerField(min_value=1, initial=1)


class CustomerForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    phone = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone number"})
    )


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add bootstrap classes & placeholders
        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter password"
        })
        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Confirm password"
        })

        # Override help text
        self.fields["password1"].help_text = (
            "Your password must be at least 8 characters long, "
            "not entirely numeric, and preferably include letters & symbols."
        )

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords didn’t match. Please try again.")
        return password2
