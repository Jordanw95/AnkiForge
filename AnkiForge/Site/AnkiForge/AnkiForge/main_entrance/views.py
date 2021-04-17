from django.shortcuts import render
from django.views.generic import TemplateView, CreateView
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect

from main_entrance.forms import MySignUpForm


from rest_auth.views import LogoutView as auth_apiLogoutView
from rest_auth.views import LoginView as auth_apiLoginView
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated


class IndexView(TemplateView):
    template_name = "main_entrance/index.html"

class MyLoginView(auth_views.LoginView):
    pass

class MyLogoutView(auth_views.LogoutView):
    pass

class MyResetPasswordView(auth_views.PasswordResetView):
    template_name = "registration/my_password_reset_form.html"
    email_template_name = 'registration/my_password_reset_email.html'
    success_url = reverse_lazy('main_entrance:password_reset_done')
    pass

class MyResetPasswordSentView(auth_views.PasswordResetDoneView):
    template_name = "registration/my_password_reset_done.html"
    pass

class MyResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "registration/my_password_reset_confirm.html"
    success_url = reverse_lazy('main_entrance:password_reset_complete')
    pass

class MyResetPasswordCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "registration/my_password_reset_complete.html"
    pass




# def mysignupview(request):
#     if request.method == 'POST':
#         form = MySignUpForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             raw_password = form.cleaned_data.get('password1')
#             user = authenticate(username=username, password=raw_password)
#             login(request, user)
#             return redirect('membership:subscribe')
#     else:
#         form = MySignUpForm()
#     return render(request, 'registration/signup.html', {'form': form})

class HowItWorksView(TemplateView):
    template_name = "main_entrance/howitworks.html"

class APILogoutView(auth_apiLogoutView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class APILoginView(auth_apiLoginView):
    pass