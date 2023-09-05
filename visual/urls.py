from django.urls import path
from django.shortcuts import redirect

from .views import ProdottoView, NuovoCampoView, ProdottoView, NuovoSottocampoView, ProdottiView, HomePageView, NuovaSocietaView
from .views import CampoSottocampoApi, ProdottiApi
from .views import LoginUserView, RegisterUserView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("", lambda request: redirect("home")),
    path("home/", HomePageView.as_view(), name="home"),
    path("prodotti/", ProdottiView.as_view(), name="prodotti"),
    path("prodotto/<str:slug>/", ProdottoView.as_view(), name="visualize"),

    path("nuova-societa", NuovaSocietaView.as_view(), name="nuova-societa"),
    path("prodotto/<str:slug>/nuovo-campo/", NuovoCampoView.as_view(), name="nuovo-campo"),
    path("nuovo-sottocampo/", NuovoSottocampoView.as_view(), name="nuovo-sottocampo"),

    path("accounts/login/", LoginUserView.as_view(), name="login"),
    path("accounts/logout/", LogoutView.as_view(), name="logout"),
    path("accounts/register/", lambda request: redirect("home"), name="register"),

    path("api/prodotto/", CampoSottocampoApi.as_view(), name="api-prodotto"),
    path("api/societa/", ProdottiApi.as_view(), name="api-prodottti")
]