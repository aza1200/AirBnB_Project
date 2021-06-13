from django.views import View
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.shortcuts import render,redirect,reverse
from django.contrib.auth import authenticate,login,logout
from . import forms

class LoginView(FormView):

    template_name = "users/login.html"
    form_class = forms.LoginForm
    success_url = reverse_lazy("core:home")
    #view 가 필요할떄 직접 호출

    def form_valid(self, form):

        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request,username=email,password=password)

        if user is not None:
            login(self.request,user)

        return super().form_valid(form)

def log_out(request):
    logout(request)
    return redirect(reverse("core:home"))
