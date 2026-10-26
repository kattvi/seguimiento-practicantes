from django.urls import path

from . import views

app_name = "practicantes"

urlpatterns = [
    path("", views.PracticanteListView.as_view(), name="lista"),
    path("nuevo/", views.PracticanteCreateView.as_view(), name="crear"),
    path("<int:pk>/", views.PracticanteDetailView.as_view(), name="detalle"),
    path("<int:pk>/editar/", views.PracticanteUpdateView.as_view(), name="editar"),
    path("<int:pk>/baja/", views.PracticanteBajaView.as_view(), name="baja"),
]
