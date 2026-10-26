from django.urls import include, path

urlpatterns = [
    path("", include("cuentas.urls")),
    path("practicantes/", include("practicantes.urls")),
]
