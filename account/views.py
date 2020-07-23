from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, AuthenticationFormByMail
from .backends import EmailBackend
from django.contrib.auth.views import LoginView


@login_required
def index(request):
    title = 'Ahoy!'
    headerImg = 'header_contact.jpg'
    return render(request, 'account/index.html', locals())

def login(request):
    form = AuthenticationFormByMail(
        data=request.POST if request.method == 'POST' else None
        )
    if request.method == 'POST':
        if form.is_valid():
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password')
            user = EmailBackend.authenticate(request, email=email, password=raw_password)
            auth.login(request, user)
            return redirect('products:index')
        else:
            # ATTENTION A LOCALS QUI£ RENVOI AUSSI LE RAWPASSWORD
            # Il est contenu dans le post mais il est enlever dans le rendu.
            return render(request, 'registration/login.html', locals())
    else:
        return render(request, 'registration/login.html', locals())

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = EmailBackend.authenticate(email=email, password=raw_password)
            auth.login(request.user)
            return redirect('products:index')
    else:
        form = SignUpForm()
    return render(request, 'account/signup.html', {'form': form})

