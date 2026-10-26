from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Practicante

Usuario = get_user_model()


class PracticanteForm(forms.ModelForm):
    """Alta y edición de un practicante junto con su cuenta de usuario."""

    nombre = forms.CharField(label="Nombre completo", max_length=100)
    correo = forms.EmailField(label="Correo electrónico", max_length=120)
    password1 = forms.CharField(
        label="Contraseña inicial",
        widget=forms.PasswordInput,
        strip=False,
        help_text="Mínimo 8 caracteres; no puede ser común ni solo números.",
    )
    password2 = forms.CharField(label="Confirmar contraseña", widget=forms.PasswordInput, strip=False)

    field_order = [
        "nombre", "correo", "matricula", "universidad", "carrera", "telefono", "supervisor",
        "fecha_inicio", "fecha_termino", "horas_requeridas", "estado", "password1", "password2",
    ]

    class Meta:
        model = Practicante
        fields = [
            "matricula", "universidad", "carrera", "telefono", "supervisor",
            "fecha_inicio", "fecha_termino", "horas_requeridas", "estado",
        ]
        widgets = {
            "fecha_inicio": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "fecha_termino": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.editando = self.instance.pk is not None
        if self.editando:
            self.initial["nombre"] = self.instance.usuario.nombre
            self.initial["correo"] = self.instance.usuario.correo
            del self.fields["password1"]
            del self.fields["password2"]
        else:
            del self.fields["estado"]  # un practicante nuevo siempre inicia como activo
        for campo in self.fields.values():
            clase = "form-select" if isinstance(campo.widget, forms.Select) else "form-control"
            campo.widget.attrs["class"] = clase

    def clean_correo(self):
        correo = self.cleaned_data["correo"].strip().lower()
        existentes = Usuario.objects.filter(correo__iexact=correo)
        if self.editando:
            existentes = existentes.exclude(pk=self.instance.usuario_id)
        if existentes.exists():
            raise ValidationError("Ya existe un usuario con este correo.")
        return correo

    def clean(self):
        datos = super().clean()
        if not self.editando:
            clave1, clave2 = datos.get("password1"), datos.get("password2")
            if clave1 and clave2 and clave1 != clave2:
                self.add_error("password2", "Las contraseñas no coinciden.")
            elif clave1:
                try:
                    validate_password(clave1)
                except ValidationError as error:
                    self.add_error("password1", error)
        return datos

    @transaction.atomic
    def save(self, commit=True):
        practicante = super().save(commit=False)
        datos = self.cleaned_data
        if self.editando:
            usuario = practicante.usuario
            usuario.nombre = datos["nombre"]
            usuario.correo = datos["correo"]
            usuario.is_active = practicante.estado != Practicante.Estado.BAJA
            usuario.save()
        else:
            usuario = Usuario.objects.create_user(
                correo=datos["correo"], password=datos["password1"], nombre=datos["nombre"]
            )
            practicante.usuario = usuario
        practicante.save()
        return practicante
