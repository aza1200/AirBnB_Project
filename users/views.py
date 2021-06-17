import os
import requests
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.shortcuts import redirect,reverse
from django.contrib.auth import authenticate,login,logout
from . import forms,models

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

class SignUpView(FormView):
    template_name =  "users/signup.html"
    form_class = forms.SignUpForm
    success_url = reverse_lazy("core:home")
    initial = {
        "first_name" : "Kim",
        "last_name"  : "Jae Hyeong",
        "email" : "jhkim@consalad.net"
    }

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request,username=email,password=password)

        if user is not None:
            login(self.request,user)

        user.verify_email()
        return super().form_valid(form)


def complete_verification(request,key):
    try:
        user = models.User.objects.get(email_secret = key)
        user.email_verified = True
        user.email_secret = ""
        user.save()
        # to do : add success message
    except models.User.DoesNotExist:
        # to do : add error message
        pass
    return redirect(reverse("core:home"))

def github_login(request):
    client_id = os.environ.get("GH_ID")
    redirect_url = "http://127.0.0.1:8000/users/login/github/callback"
    return redirect(f"https://github.com/login/oauth/authorize?client_id={client_id}"
                    f"&redirect_url={redirect_url}"
                    f"&scope=read:user")

def github_callback(request):
    client_id     = os.environ.get("GH_ID")
    client_secret = os.environ.get("GH_SECRET")
    code = request.GET.get("code",None)
    if code is not None:
        request = requests.post(f"https://github.com/login/oauth/access_token"
                                 f"?client_id={client_id}"
                                 f"&client_secret={client_secret}"
                                 f"&code={code}",
                                 headers ={"Accept":"application/json"},
                                 )
        print(request.json())
    else:
        return redirect(reverse("core:home"))


#<QueryDict: {'code': ['c0623b0633a0e66e5bc9']}>

# 1. github redirect
# 2. get access token
# 3. access oken 으로 user 받아오기