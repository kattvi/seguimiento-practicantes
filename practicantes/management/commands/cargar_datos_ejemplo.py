from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from practicantes.models import Practicante

Usuario = get_user_model()

# Datos de ejemplo SOLO para pruebas y demostraciones en tu computadora.
CORREO_ADMIN = "admin@ejemplo.com"
CLAVE_EJEMPLO = "Ejemplo-2026-Cambiar"

PRACTICANTES = [
    ("Ana Torres Ruiz", "Universidad de Ejemplo", "Desarrollo de Software", "activo"),
    ("Luis Hernández Pech", "Instituto de Ejemplo", "Ingeniería en Sistemas", "activo"),
    ("María Cruz Canul", "Universidad de Ejemplo", "Diseño Gráfico", "activo"),
    ("Jorge Mena Dzul", "Instituto de Ejemplo", "Administración", "activo"),
    ("Sofía Ramírez Poot", "Universidad de Ejemplo", "Desarrollo de Software", "activo"),
    ("Diego Castillo Uc", "Universidad de Ejemplo", "Ingeniería en Sistemas", "terminado"),
    ("Valeria Chan May", "Instituto de Ejemplo", "Psicología", "activo"),
    ("Carlos Aguilar Tun", "Universidad de Ejemplo", "Desarrollo de Software", "activo"),
    ("Daniela Pérez Koh", "Instituto de Ejemplo", "Administración", "baja"),
    ("Mario Euán Balam", "Universidad de Ejemplo", "Ingeniería en Sistemas", "activo"),
    ("Paola Sosa Cime", "Instituto de Ejemplo", "Diseño Gráfico", "activo"),
    ("Andrés Pool Ek", "Universidad de Ejemplo", "Desarrollo de Software", "terminado"),
]


class Command(BaseCommand):
    help = "Crea un administrador y 12 practicantes de ejemplo (solo para pruebas y demostraciones)."

    @transaction.atomic
    def handle(self, *args, **opciones):
        if Usuario.objects.filter(correo=CORREO_ADMIN).exists():
            self.stdout.write("Los datos de ejemplo ya existen; no se creó nada nuevo.")
            return

        Usuario.objects.create_user(
            correo=CORREO_ADMIN, password=CLAVE_EJEMPLO, nombre="Administrador de Ejemplo",
            rol=Usuario.Rol.ADMINISTRADOR,
        )
        for numero, (nombre, universidad, carrera, estado) in enumerate(PRACTICANTES, start=1):
            usuario = Usuario.objects.create_user(
                correo=f"practicante{numero:02d}@ejemplo.com",
                password=CLAVE_EJEMPLO,
                nombre=nombre,
                is_active=estado != "baja",
            )
            Practicante.objects.create(
                usuario=usuario,
                matricula=f"EJ-{numero:04d}",
                universidad=universidad,
                carrera=carrera,
                telefono=f"999000{numero:04d}",
                supervisor="Supervisor de Ejemplo",
                fecha_inicio=date(2026, 8, 31),
                fecha_termino=date(2027, 3, 17),
                estado=estado,
            )

        self.stdout.write(self.style.SUCCESS("Datos de ejemplo creados."))
        self.stdout.write(f"Administrador:  {CORREO_ADMIN}")
        self.stdout.write(f"Contraseña (todas las cuentas de ejemplo): {CLAVE_EJEMPLO}")
        self.stdout.write("Estos datos son solo para pruebas; no los uses en un sistema real.")
