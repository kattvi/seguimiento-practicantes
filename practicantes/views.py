from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from cuentas.mixins import AdministradorRequeridoMixin

from .forms import PracticanteForm
from .models import Practicante


class PracticanteListView(AdministradorRequeridoMixin, ListView):
    """Consulta: lista de practicantes con búsqueda por nombre o matrícula (RF-06)."""

    model = Practicante
    template_name = "practicantes/lista.html"
    context_object_name = "practicantes"
    paginate_by = 10

    def get_queryset(self):
        practicantes = Practicante.objects.select_related("usuario")
        busqueda = self.request.GET.get("q", "").strip()
        estado = self.request.GET.get("estado", "")
        if busqueda:
            practicantes = practicantes.filter(
                Q(usuario__nombre__icontains=busqueda) | Q(matricula__icontains=busqueda)
            )
        if estado in Practicante.Estado.values:
            practicantes = practicantes.filter(estado=estado)
        return practicantes

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        busqueda = self.request.GET.get("q", "").strip()
        estado = self.request.GET.get("estado", "")
        filtros = {clave: valor for clave, valor in (("q", busqueda), ("estado", estado)) if valor}
        contexto.update(
            q=busqueda,
            estado=estado,
            estados=Practicante.Estado.choices,
            filtros=urlencode(filtros),
        )
        return contexto


class PracticanteDetailView(AdministradorRequeridoMixin, DetailView):
    model = Practicante
    template_name = "practicantes/detalle.html"
    context_object_name = "practicante"


class PracticanteCreateView(AdministradorRequeridoMixin, SuccessMessageMixin, CreateView):
    """Alta de un practicante (RF-03)."""

    model = Practicante
    form_class = PracticanteForm
    template_name = "practicantes/formulario.html"
    success_message = "Practicante registrado correctamente."

    def get_success_url(self):
        return reverse("practicantes:detalle", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto.update(titulo="Registrar practicante", boton="Guardar", cancelar=reverse("practicantes:lista"))
        return contexto


class PracticanteUpdateView(AdministradorRequeridoMixin, SuccessMessageMixin, UpdateView):
    """Edición de los datos de un practicante (RF-04)."""

    model = Practicante
    form_class = PracticanteForm
    template_name = "practicantes/formulario.html"
    success_message = "Los datos del practicante se actualizaron."

    def get_success_url(self):
        return reverse("practicantes:detalle", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto.update(
            titulo="Editar practicante",
            boton="Guardar cambios",
            cancelar=reverse("practicantes:detalle", args=[self.object.pk]),
        )
        return contexto


class PracticanteBajaView(AdministradorRequeridoMixin, DetailView):
    """Baja lógica de un practicante (RF-05): pide confirmación y no borra su historial."""

    model = Practicante
    template_name = "practicantes/confirmar_baja.html"
    context_object_name = "practicante"

    def post(self, request, *args, **kwargs):
        practicante = self.get_object()
        if practicante.estado == Practicante.Estado.BAJA:
            messages.info(request, "El practicante ya estaba dado de baja.")
        else:
            practicante.dar_de_baja()
            messages.success(request, f"{practicante.usuario.nombre} fue dado de baja. Su historial se conserva.")
        return redirect("practicantes:lista")
