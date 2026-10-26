from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def _crear(self, correo, password, **extra):
        if not correo:
            raise ValueError("El correo es obligatorio.")
        usuario = self.model(correo=self.normalize_email(correo), **extra)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_user(self, correo, password=None, **extra):
        extra.setdefault("rol", Usuario.Rol.PRACTICANTE)
        return self._crear(correo, password, **extra)

    def create_superuser(self, correo, password=None, **extra):
        extra.setdefault("rol", Usuario.Rol.ADMINISTRADOR)
        extra.setdefault("is_superuser", True)
        return self._crear(correo, password, **extra)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Persona que inicia sesión en el sistema (tabla `usuario` del diseño)."""

    class Rol(models.TextChoices):
        ADMINISTRADOR = "administrador", "Administrador"
        PRACTICANTE = "practicante", "Practicante"

    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField("nombre", max_length=100)
    correo = models.EmailField("correo electrónico", max_length=120, unique=True)
    password = models.CharField("contraseña", max_length=255, db_column="contrasena_hash")
    rol = models.CharField(max_length=15, choices=Rol.choices, default=Rol.PRACTICANTE)
    is_active = models.BooleanField("activo", default=True, db_column="activo")

    objects = UsuarioManager()

    USERNAME_FIELD = "correo"
    REQUIRED_FIELDS = ["nombre"]

    class Meta:
        db_table = "usuario"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(rol__in=["administrador", "practicante"]),
                name="ck_usuario_rol",
            ),
        ]

    def __str__(self):
        return self.nombre

    @property
    def es_administrador(self):
        return self.rol == self.Rol.ADMINISTRADOR

    @property
    def is_staff(self):
        return self.es_administrador
