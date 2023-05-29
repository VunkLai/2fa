from http import HTTPStatus

from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

import pyotp
from authentication.models import User


def register(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return render(request, "authentication/register.html")
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        User.objects.create_user(username, None, password)
        return redirect("/auth/sign_in")
    return HttpResponse("", status=HTTPStatus.METHOD_NOT_ALLOWED)


def sign_in(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/auth/two_factor")
        return render(request, "authentication/sign_in.html")
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect("/auth/two_factor")
        return render(
            request,
            "authentication/sign_in.html",  # todo: error handler
            status=HTTPStatus.BAD_REQUEST,
        )
    return HttpResponse("", status=HTTPStatus.METHOD_NOT_ALLOWED)


def sign_out(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        logout(request)
    response = redirect("/auth/sign_in")
    expired_time = timezone.localtime() - timezone.timedelta(minutes=5)
    response.set_cookie("auth_token", "", expires=expired_time.timestamp())
    return response


def two_factor(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("/auth/sign_in")

    if request.method == "GET":
        return render(request, "authentication/two_factor.html")
    if request.method == "POST":
        code = request.POST["code"]
        totp = pyotp.TOTP(request.user.password)
        if totp.verify(code):
            # todo: redirect to $request_uri
            response = redirect("/auth/sign_in")
            # todo: Create token
            response.set_cookie(
                "auth_token", "mock-token", httponly=True, max_age=24 * 60 * 60
            )
            return response
        return HttpResponse(
            request,
            "authentication/two_factor.html",  # todo: invalid verify
            status=HTTPStatus.FORBIDDEN,
        )
    return HttpResponse("", status=HTTPStatus.METHOD_NOT_ALLOWED)


def qr_code(request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        return redirect("/auth/sign_in")

    if request.method == "GET":
        return render(request, "authentication/qr_code.html")
    return HttpResponse("", status=HTTPStatus.METHOD_NOT_ALLOWED)
