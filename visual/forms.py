from typing import Any, Dict
from django import forms

from django.contrib.auth import password_validation
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

# from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.forms import *
from django.contrib.auth.password_validation import (
    UserAttributeSimilarityValidator, 
    MinimumLengthValidator, 
    CommonPasswordValidator, 
    get_default_password_validators)

from .models import Sottocampo, Campo, Pezzo, Orario, Prodotto, CustomUser
from decimal import Decimal

class CustomUserCreationForm(forms.ModelForm):
    error_messages_password_egual = {
            "password_mismatch": _("The two password fields didn’t match."),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.password_validators_list = [
            UserAttributeSimilarityValidator(["nome", "cognome", "email"]),
            MinimumLengthValidator(2)
        ]

        self.fields["email"].widget.attrs.update({'autocomplete': 'off'})
        self.fields["nome"].widget.attrs.update({'autocomplete': 'off'})
        self.fields["cognome"].widget.attrs.update({'autocomplete': 'off'})


    password1 = forms.CharField(
        label=_("Password"),
        strip=False,                                                            # spazi bianchi non rimossi
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        # help_text=password_validation.password_validators_help_text_html(),
    )

    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,                                                            # spazi bianchi non rimossi
        # help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        model = CustomUser
        fields = ["email", "nome", "cognome", "password1", "password2"]

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            print("erroraccio")
            raise ValidationError(
                self.error_messages_password_egual["password_mismatch"],
                code="password_mismatch",
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get("password2")
        if password:
            try:
                password_validation.validate_password(password, self.instance, self.password_validators_list)
            except ValidationError as error:
                self.add_error("password2", error)
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class CustomUserAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={"autofocus": True}))

    class Meta:
        model = CustomUser
        fields = ["username", "password"]

class CampoForm(forms.ModelForm):
    class Meta:
        model = Campo
        fields = ['nome']
        widgets = {
            'nome': forms.TextInput(attrs={'autocomplete': 'off'})  # è scomodo
        }

class SottocampoForm(forms.ModelForm):
    class Meta:
        model = Sottocampo
        fields = "__all__"

class Sottocampo_Pezzo(forms.ModelForm):
    nome = forms.CharField(max_length=120, widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    # ruolo = forms.ChoiceField(choices=(
    #     ("Spesa", "spesa"), ("Guadango", "guadagno")
    # ))

    costo = forms.DecimalField(label="Costo (€)", min_value=0.0)

    class Meta:
        model = Pezzo
        fields = "__all__"

class Sottocampo_Orario(forms.ModelForm):
    nome = forms.CharField(max_length=120, widget=forms.TextInput(attrs={'autocomplete': 'off'}))
    # ruolo = forms.ChoiceField(choices=(
    #     ("Spesa", "spesa"), ("Guadango", "guadagno")
    # ))

    tariffa = forms.DecimalField(label="Tariffa (€)", min_value=0.0)
    ore = forms.DurationField(widget=forms.TextInput(attrs={"autocomplete": "off"}))

    class Meta:
        model = Orario
        fields = "__all__"

class ProdottoForm(forms.ModelForm):
    class Meta:
        model = Prodotto
        fields = ["nome"]
        widgets = {
            'nome': forms.TextInput(attrs={'autocomplete': 'off'})  # è scomodo
        }