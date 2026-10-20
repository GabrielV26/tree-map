from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from chart import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.index, name="index"),
    path("api/crypto/", views.get_data, name="get_data"),
    path("save/", views.save_data, name="save_data"),
    path("delete_data/<int:id>/", views.delete_data, name="delete_data"),
]
