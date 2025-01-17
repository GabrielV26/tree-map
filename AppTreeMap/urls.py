"""
URL configuration for AppTreeMap project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from chart import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/crypto/', views.get_data, name='get_data'),
    path('save/', views.save_data, name='save_data'),
    path('delete_data/<int:id>/', views.delete_data, name='delete_data'),
]
