import os
import requests
from django.contrib.auth.views import PasswordChangeView
from django.views.generic import FormView,DetailView,UpdateView
from django.urls import reverse_lazy
from django.shortcuts import redirect,reverse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from . import forms,models,mixins

class LoginView(mixins.LoggedOutOnlyView,FormView):

    template_name = "users/login.html"
    form_class = forms.LoginForm
    #view 가 필요할떄 직접 호출

    def form_valid(self, form):

        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request,username=email,password=password)

        if user is not None:
            login(self.request,user)

        return super().form_valid(form)

    def get_success_url(self):
        next_arg = self.request.GET.get("next")

        if next_arg is not None:
            return next_arg
        else:
            return reverse("core:home")

def log_out(request):
    messages.info(request,f'See you later')
    logout(request)
    return redirect(reverse("core:home"))

class SignUpView(mixins.LoggedOutOnlyView,FormView):
    template_name =  "users/signup.html"
    form_class = forms.SignUpForm
    success_url = reverse_lazy("core:home")

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

class GithubException(Exception):
    pass

def github_callback(request):
    try:
        client_id     = os.environ.get("GH_ID")
        client_secret = os.environ.get("GH_SECRET")
        code = request.GET.get("code",None)
        if code is not None:
            token_request = requests.post(f"https://github.com/login/oauth/access_token"
                                     f"?client_id={client_id}"
                                     f"&client_secret={client_secret}"
                                     f"&code={code}",
                                     headers ={"Accept":"application/json"},
                                     )
            token_json = token_request.json()
            error = token_json.get("error",None)
            if error is not None:
                raise GithubException("Can't get access token")
            else:
                access_token = token_json.get("access_token")
                profile_request = requests.get("https://api.github.com/user",
                                           headers={
                                               "Authorization":f"token {access_token}",
                                               "Accept" : "application/json",
                                                },
                                            )
                profile_json = profile_request.json()
                username = profile_json.get('login',None)
                if username is not None:
                    name = profile_json.get('name')
                    email = profile_json.get('email')
                    bio = profile_json.get('bio')

                    if name is None: name = username
                    if bio is None: bio = ""
                    if email is None: email = name

                    try:
                        user = models.User.objects.get(email=email)
                        if user.login_method != models.User.LOGIN_GITHUB:
                            raise GithubException(f"Please log in with: {user.login_method}")
                            #trying to log in
                    except models.User.DoesNotExist:
                        user = models.User.objects.create(
                            email=email,first_name = name,
                            username=email,bio=bio,
                            login_method = models.User.LOGIN_GITHUB,
                            email_verified = True
                        )
                        user.set_unusable_password()
                        user.save()
                    login(request,user)
                    message.success(requests,f"welcome back {user.first_name}")
                    return redirect(reverse("core:home"))
                else:
                    raise GithubException("Can't get your profile")
        else:
            raise GithubException("Can't get code")
    except GithubException as e:
        messages.error(request,e)
        return redirect(reverse("users:login"))

def kakao_login(request):
    client_id = os.environ.get("KAKAO_ID")
    redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=account_email"
    )

class KakaoException(Exception):
    pass

def kakao_callback(request):
    try:
        code = request.GET.get("code")

        client_id = os.environ.get("KAKAO_ID")
        redirect_uri = "http://127.0.0.1:8000/users/login/kakao/callback"
        token_request = requests.get(f"https://kauth.kakao.com/oauth/token?"
                                     f"grant_type=authorization_code&"
                                     f"client_id={client_id}&"
                                     f"redirect_uri={redirect_uri}&"
                                     f"code={code}")

        token_json = token_request.json()
        error = token_json.get("error",None)
        #print(token_json)
        if error is not None:
            raise KakaoException("Can't get authorization code")
        access_token = token_json.get("access_token")
        profile_request = requests.get("https://kapi.kakao.com/v2/user/me",
                                       headers={"Authorization": f"Bearer {access_token}" },
                                       )
        profile_json = profile_request.json()
        #print(profile_json)
        properties = profile_json.get("kakao_account")
        email = properties.get("email")
        #print(properties,email)
        if email is None:
            #print("email 값이 없습니다")
            raise KakaoException("Please also give me your email")
        nickname =properties.get("profile").get("nickname")
        profile_image = properties.get("profile").get("profile_image_url")
        try:
            user = models.User.objects.get(email=email)
            if user.login_method != models.User.LOGIN_KAKAO:
                raise KakaoException(f"Please log in with: {user.login_method}")
        except models.User.DoesNotExist:
            user = models.User.objects.create(
                email = email,
                username = email,
                first_name = nickname,
                login_method = models.User.LOGIN_KAKAO,
                email_verified = True
            )
            user.set_unusable_password()
            user.save()

            if profile_image is not None:
                photo_request = requests.get(profile_image)
                user.avatar.save(f"{nickname}-avatar",
                                 ContentFile(photo_request.content)
                )
        login(request,user)
        messages.success(request,f"Welcome back {user.first_name}")
        return redirect(reverse("core:home"))
    except KakaoException as e:
        messages.error(request,e)
        return redirect(reverse("users:login"))

class UserProfileView(DetailView):

    model = models.User
    context_object_name = 'user_obj'


class UpdateUserView(
    mixins.LoggedInOnlyView,
    SuccessMessageMixin,UpdateView
):
    model = models.User
    template_name="users/update_profile.html"
    fields= (
        "email",
        "first_name",
        "last_name",
        "gender",
        "bio",
        "birthdate",
        "language",
        "currency",
    )
    success_message = "Profile Updated"

    def get_object(self, queryset=None):
        return self.request.user

    def get_form(self,form_class=None):
        form =  super().get_form(form_class=form_class)
        form.fields["first_name"].widget.attrs = {"placeholder": "First name"}
        form.fields["birthdate"].widget.attrs = {"placeholder": "Birthdate"}
        return form

class UpdatePasswordView(
    mixins.LoggedInOnlyView,
    mixins.EmailLoginOnlyView,
    SuccessMessageMixin,
    PasswordChangeView
):

    template_name = "users/update_password.html"

    def get_form(self,form_class=None):
        form =  super().get_form(form_class=form_class)
        form.fields['old_password'].widget.attrs={'placeholder':"Old Password"}
        form.fields["new_password1"].widget.attrs={"placeholder":"New password"}
        form.fields["new_password2"].widget.attrs = {"placeholder": "Pasword Check"}
        return form

    def get_success_url(self):
        return self.request.user.get_absolute_url()


@login_required
def switch_hosting(request):
    try:
        del request.session["is_hosting"]
    except KeyError:
        request.session["is_hosting"] = True
    return redirect(reverse("core:home"))


    # def form_valid(self,form):
    #
    #     email = form.cleaned_data.get("email")
    #     self.object.username = email
    #     self.object.save()
    #
    #     return super().form_valid(form)

#<QueryDict: {'code': ['c0623b0633a0e66e5bc9']}>

# 1. github redirect
# 2. get access token
# 3. access oken 으로 user 받아오기