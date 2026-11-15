from django.urls import path
from . import views

app_name = "emails"

urlpatterns = [
    path("oauth2/", views.oauth2_init, name="oauth2_init"),
    path("oauth2callback", views.oauth2_callback, name="oauth2_callback"),
]