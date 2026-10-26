from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction


class Practicante(models.Model):
    """Estudiante que realiza sus prácticas (tabla `practicante` del diseño)."""

    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        TERMINADO = "terminado", "Terminado"
        BAJA = "baja", "Baja"

    id_practicante = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        db_column="id_usuario",
        related_name="practicante",
    )
    matricula = models.CharField("matrícula", max_length=30, unique=True)
    universidad = models.CharField(max_length=100)
    carrera = models.CharField(max_length=100)
    telefono = models.CharField("teléfono", max_length=20, blank=True)
    supervisor = models.CharField(max_length=100)
    fecha_inicio = models.DateField("fecha de inicio")
    fecha_termino = models.DateField("fecha de término")
    horas_requeridas = models.PositiveSmallIntegerField(
        "horas requeridas", default=480, validators=[MinValueValidator(1)]
    )
    estado = models.CharField(max_length=10, choices=Estado.choices, default=Estado.ACTIVO)

    class Meta:
        db_table = "practicante"
        ordering = ["usuario__nombre"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(fecha_termino__gte=models.F("fecha_inicio")),
                name="ck_practicante_fechas",
            ),
            models.CheckConstraint(
                condition=models.Q(horas_requeridas__gt=0),
                name="ck_practicante_horas",
            ),
            models.CheckConstraint(
                condition=models.Q(estado__in=["activo", "terminado", "baja"]),
                name="ck_practicante_estado",
            ),
        ]

    def __str__(self):
        return f"{self.usuario.nombre} ({self.matricula})"

    def clean(self):
        if self.fecha_inicio and self.fecha_termino and self.fecha_termino < self.fecha_inicio:
            raise ValidationError(
                {"fecha_termino": "La fecha de término no puede ser anterior a la fecha de inicio."}
            )

    @transaction.atomic
    def dar_de_baja(self):
        """Baja lógica (RN-05): cambia el estado y desactiva la cuenta; no borra nada."""
        self.estado = self.Estado.BAJA
        self.save(update_fields=["estado"])
        self.usuario.is_active = False
        self.usuario.save(update_fields=["is_active"])
