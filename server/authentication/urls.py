from django.urls import path

from authentication import views

urlpatterns = [
    path("register", views.register),
    path("sign_in", views.sign_in),
    path("sign_out", views.sign_out),
    path("two_factor", views.two_factor),
    path("two_factor/qr_code", views.qr_code),
]
