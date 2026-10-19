from django.contrib import admin
from django.urls import path

from chart import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.index, name="index"),
    path("api/crypto/", views.get_data, name="get_data"),
    path("save/", views.save_data, name="save_data"),
    path("delete_data/<int:id>/", views.delete_data, name="delete_data"),
]
