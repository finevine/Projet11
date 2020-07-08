from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from .backends import EmailBackend


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Requis.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )
        labels = {
            'username': _("Nom d'utilisateur"),
            'email': _("Adresse email valide"),
        }
        help_texts = {
        }


class AuthenticationFormByMail(AuthenticationForm):
    email = forms.EmailField(
        label='Email',
        widget=forms.TextInput(attrs={'autofocus': True})
    )

    class Meta:
        fields = ('email', 'password')
        labels = {
            'email': _("Adresse email"),
            'password': _("Mot de passe"),
        }
        help_texts = {
        }

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            self.user_cache = EmailBackend.authenticate(
                self.request, email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
