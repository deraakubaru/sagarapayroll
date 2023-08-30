"""
URL configuration for Penggajian project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view as swagger_get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from gaji_app.views import DivisiView, LoginView, RegisterView, UserRetrieveUpdateDeleteView, UpdateProfileView, AbsenView, GajiView, GajiTetapList, AbsencelImportView, UserDataImportView, DivisiDataImportView, GajiFreelanceList, GajiRetrieveUpdateDeleteView, KaryawanTetapList, KaryawanFreelanceList, GajiFreelanceRUDView, GajiFreelanceCreateView, LogoutAPI
from gaji_app import views


schema_view = swagger_get_schema_view(
    openapi.Info(
        title="Penggajian",
        default_version='1.0.0',
        description="API doc of Sagara's Payroll"
    ),
    public=True,
    permission_classes=[permissions.AllowAny]
)

urlpatterns = [
    #Layout
    path('', views.LoginView.login_view, name = "login"),
    path('home', views.LoginView.dashboard_view, name = "dashboard"),
    
    path('admin/', admin.site.urls),
    # swagger
    path('swagger/', schema_view.with_ui(
        'swagger', cache_timeout=0), name="schema-swagger-ui"),
    path('api-auth', include('rest_framework.urls')),
    
    #Divisi
    path('divisi', DivisiView.as_view(), name = 'divisi'),
    #user
    path('login/', LoginView.as_view(), name='login-api'),
    path('logout', LogoutAPI.as_view(), name = 'logout-api'),
    path('registrasi', RegisterView.as_view(), name='user-regist'),
    path('users/<uuid:pk>', UserRetrieveUpdateDeleteView.as_view(), name='user-detail'),
    
    #Karyawan
    path('karyawan/<uuid:user_id>', UpdateProfileView.as_view(), name='karyawan-detail'),
    path('data-karyawan-tetap', KaryawanTetapList.as_view(), name='karyawan-tetap'),
    path('data-karyawan-freelance', KaryawanFreelanceList.as_view(), name='karyawan-freelance'),
    
    #Gaji
    path('api/get-gaji/<uuid:pk>', GajiRetrieveUpdateDeleteView.as_view(), name='gaji-detail'),
    path('data-gaji-tetap', GajiTetapList.as_view(), name='gaji-tetap'),
    path('data-gaji-freelancer', GajiFreelanceList.as_view(), name='gaji-freelancer'),
    path('data-gaji-freelancer/update/<uuid:pk>', GajiFreelanceRUDView.as_view(), name='update-gaji-freelancer'),
    path('create_absen', AbsenView.as_view(), name='insert-absen'),
    path('input-gaji', GajiView.as_view(), name='insert-data-gaji'),
    path('input-gaji-freelance', GajiFreelanceCreateView.as_view(), name='insert-data-gaji-freelance'),
    
    #ImportData
    path('import_absen', AbsencelImportView.as_view(), name='import_data_absen'),
    path('import_user', UserDataImportView.as_view(), name='import_data_user'),
    path('import_divisi', DivisiDataImportView.as_view(), name='import_data_divisi'),
]
