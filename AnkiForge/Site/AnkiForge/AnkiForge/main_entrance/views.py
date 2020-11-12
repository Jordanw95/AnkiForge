
from django.shortcuts import render
from django.views.generic import TemplateView, CreateView
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect

from main_entrance.forms import MySignUpForm


class IndexView(TemplateView):
    template_name = "main_entrance/index.html"

class MyLoginView(auth_views.LoginView):
    pass

class MyLogoutView(auth_views.LogoutView):
    pass

def mysignupview(request):
    if request.method == 'POST':
        form = MySignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('main_entrance:login')
    else:
        form = MySignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

class HowItWorksView(TemplateView):
    template_name = "main_entrance/howitworks.html"
