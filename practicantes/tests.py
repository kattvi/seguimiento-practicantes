from datetime import date
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse

from .models import Practicante

Usuario = get_user_model()
CLAVE = "Cl4ve-de-prueba-2026"


def crear_admin():
    return Usuario.objects.create_user(
        correo="admin@prueba.com", password=CLAVE, nombre="Admin Prueba", rol=Usuario.Rol.ADMINISTRADOR
    )


def crear_practicante(numero=1, **extra):
    usuario = Usuario.objects.create_user(
        correo=f"practicante{numero}@prueba.com", password=CLAVE, nombre=f"Practicante {numero:02d}"
    )
    datos = dict(
        usuario=usuario,
        matricula=f"M{numero:04d}",
        universidad="Universidad de Prueba",
        carrera="Desarrollo de Software",
        supervisor="Supervisor Prueba",
        fecha_inicio=date(2026, 8, 31),
        fecha_termino=date(2027, 3, 17),
    )
    datos.update(extra)
    return Practicante.objects.create(**datos)


def datos_alta(**extra):
    datos = {
        "nombre": "Ana Prueba",
        "correo": "ana@prueba.com",
        "matricula": "A0001",
        "universidad": "Universidad de Prueba",
        "carrera": "Desarrollo de Software",
        "telefono": "9990000000",
        "supervisor": "Supervisor Prueba",
        "fecha_inicio": "2026-08-31",
        "fecha_termino": "2027-03-17",
        "horas_requeridas": 480,
        "password1": CLAVE,
        "password2": CLAVE,
    }
    datos.update(extra)
    return datos


def datos_edicion(practicante, **extra):
    datos = {
        "nombre": practicante.usuario.nombre,
        "correo": practicante.usuario.correo,
        "matricula": practicante.matricula,
        "universidad": practicante.universidad,
        "carrera": practicante.carrera,
        "telefono": practicante.telefono,
        "supervisor": practicante.supervisor,
        "fecha_inicio": practicante.fecha_inicio.isoformat(),
        "fecha_termino": practicante.fecha_termino.isoformat(),
        "horas_requeridas": practicante.horas_requeridas,
        "estado": practicante.estado,
    }
    datos.update(extra)
    return datos


class ModeloTests(TestCase):
    def test_valores_por_defecto(self):
        practicante = crear_practicante()
        self.assertEqual(practicante.horas_requeridas, 480)
        self.assertEqual(practicante.estado, Practicante.Estado.ACTIVO)
        self.assertIn("Practicante 01", str(practicante))

    def test_la_base_de_datos_rechaza_fechas_invertidas(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            crear_practicante(fecha_inicio=date(2027, 1, 1), fecha_termino=date(2026, 1, 1))

    def test_la_base_de_datos_rechaza_horas_en_cero(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            crear_practicante(horas_requeridas=0)

    def test_dar_de_baja_desactiva_la_cuenta_sin_borrar_nada(self):
        practicante = crear_practicante()
        practicante.dar_de_baja()
        practicante.refresh_from_db()
        practicante.usuario.refresh_from_db()
        self.assertEqual(practicante.estado, Practicante.Estado.BAJA)
        self.assertFalse(practicante.usuario.is_active)
        self.assertEqual(Practicante.objects.count(), 1)


class AccesoTests(TestCase):
    def setUp(self):
        self.practicante = crear_practicante()
        self.urls = [
            reverse("practicantes:lista"),
            reverse("practicantes:crear"),
            reverse("practicantes:detalle", args=[self.practicante.pk]),
            reverse("practicantes:editar", args=[self.practicante.pk]),
            reverse("practicantes:baja", args=[self.practicante.pk]),
        ]

    def test_sin_sesion_se_redirige_al_login(self):
        for url in self.urls:
            with self.subTest(url=url):
                respuesta = self.client.get(url)
                self.assertRedirects(respuesta, f"{reverse('login')}?next={url}")

    def test_un_practicante_recibe_403(self):
        self.client.force_login(self.practicante.usuario)
        for url in self.urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 403)

    def test_el_administrador_puede_entrar(self):
        self.client.force_login(crear_admin())
        for url in self.urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)


class AltaTests(TestCase):
    def setUp(self):
        self.client.force_login(crear_admin())
        self.url = reverse("practicantes:crear")

    def test_alta_valida_crea_usuario_y_practicante(self):
        respuesta = self.client.post(self.url, datos_alta())
        practicante = Practicante.objects.get(matricula="A0001")
        self.assertRedirects(respuesta, reverse("practicantes:detalle", args=[practicante.pk]))
        self.assertEqual(practicante.horas_requeridas, 480)
        self.assertEqual(practicante.estado, Practicante.Estado.ACTIVO)
        usuario = practicante.usuario
        self.assertEqual(usuario.correo, "ana@prueba.com")
        self.assertEqual(usuario.rol, Usuario.Rol.PRACTICANTE)
        self.assertTrue(usuario.check_password(CLAVE))

    def test_el_correo_se_guarda_en_minusculas(self):
        self.client.post(self.url, datos_alta(correo="ANA@Prueba.com"))
        self.assertTrue(Usuario.objects.filter(correo="ana@prueba.com").exists())

    def test_fecha_de_termino_anterior_al_inicio(self):
        respuesta = self.client.post(self.url, datos_alta(fecha_termino="2026-08-01"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("fecha_termino", respuesta.context["form"].errors)
        self.assertFalse(Practicante.objects.exists())

    def test_matricula_duplicada(self):
        crear_practicante(matricula="A0001")
        respuesta = self.client.post(self.url, datos_alta())
        self.assertIn("matricula", respuesta.context["form"].errors)

    def test_correo_duplicado(self):
        crear_practicante(1)
        respuesta = self.client.post(self.url, datos_alta(correo="practicante1@prueba.com"))
        self.assertIn("correo", respuesta.context["form"].errors)

    def test_contrasenas_distintas(self):
        respuesta = self.client.post(self.url, datos_alta(password2="Otra-clave-2026"))
        self.assertIn("password2", respuesta.context["form"].errors)
        self.assertFalse(Practicante.objects.exists())

    def test_contrasena_debil(self):
        respuesta = self.client.post(self.url, datos_alta(password1="12345678", password2="12345678"))
        self.assertIn("password1", respuesta.context["form"].errors)

    def test_horas_requeridas_deben_ser_mayores_que_cero(self):
        respuesta = self.client.post(self.url, datos_alta(horas_requeridas=0))
        self.assertIn("horas_requeridas", respuesta.context["form"].errors)

    def test_el_formulario_de_alta_no_pide_estado(self):
        respuesta = self.client.get(self.url)
        self.assertNotIn("estado", respuesta.context["form"].fields)


class EdicionTests(TestCase):
    def setUp(self):
        self.client.force_login(crear_admin())
        self.practicante = crear_practicante()
        self.url = reverse("practicantes:editar", args=[self.practicante.pk])

    def test_editar_actualiza_practicante_y_usuario(self):
        datos = datos_edicion(
            self.practicante, nombre="Nombre Nuevo", correo="nuevo@prueba.com", carrera="Ingeniería en Sistemas"
        )
        respuesta = self.client.post(self.url, datos)
        self.assertRedirects(respuesta, reverse("practicantes:detalle", args=[self.practicante.pk]))
        self.practicante.refresh_from_db()
        self.practicante.usuario.refresh_from_db()
        self.assertEqual(self.practicante.carrera, "Ingeniería en Sistemas")
        self.assertEqual(self.practicante.usuario.nombre, "Nombre Nuevo")
        self.assertEqual(self.practicante.usuario.correo, "nuevo@prueba.com")

    def test_editar_no_cambia_la_contrasena(self):
        self.client.post(self.url, datos_edicion(self.practicante, nombre="Otro Nombre"))
        self.practicante.usuario.refresh_from_db()
        self.assertTrue(self.practicante.usuario.check_password(CLAVE))

    def test_conservar_el_mismo_correo_es_valido(self):
        respuesta = self.client.post(self.url, datos_edicion(self.practicante))
        self.assertEqual(respuesta.status_code, 302)

    def test_no_se_puede_usar_el_correo_de_otro_usuario(self):
        crear_practicante(2)
        respuesta = self.client.post(self.url, datos_edicion(self.practicante, correo="practicante2@prueba.com"))
        self.assertIn("correo", respuesta.context["form"].errors)

    def test_cambiar_el_estado_a_baja_desactiva_la_cuenta_y_activo_la_reactiva(self):
        self.client.post(self.url, datos_edicion(self.practicante, estado="baja"))
        self.practicante.usuario.refresh_from_db()
        self.assertFalse(self.practicante.usuario.is_active)
        self.client.post(self.url, datos_edicion(self.practicante, estado="activo"))
        self.practicante.usuario.refresh_from_db()
        self.assertTrue(self.practicante.usuario.is_active)

    def test_el_formulario_de_edicion_no_pide_contrasena(self):
        respuesta = self.client.get(self.url)
        self.assertNotIn("password1", respuesta.context["form"].fields)
        self.assertEqual(respuesta.context["form"].initial["nombre"], "Practicante 01")


class BajaTests(TestCase):
    def setUp(self):
        self.client.force_login(crear_admin())
        self.practicante = crear_practicante()
        self.url = reverse("practicantes:baja", args=[self.practicante.pk])

    def test_get_muestra_la_confirmacion_y_no_cambia_nada(self):
        respuesta = self.client.get(self.url)
        self.assertContains(respuesta, "Confirmar baja")
        self.practicante.refresh_from_db()
        self.assertEqual(self.practicante.estado, Practicante.Estado.ACTIVO)

    def test_post_da_de_baja_sin_borrar(self):
        respuesta = self.client.post(self.url)
        self.assertRedirects(respuesta, reverse("practicantes:lista"))
        self.practicante.refresh_from_db()
        self.practicante.usuario.refresh_from_db()
        self.assertEqual(self.practicante.estado, Practicante.Estado.BAJA)
        self.assertFalse(self.practicante.usuario.is_active)
        self.assertEqual(Practicante.objects.count(), 1)

    def test_dar_de_baja_dos_veces_avisa(self):
        self.client.post(self.url)
        respuesta = self.client.post(self.url, follow=True)
        self.assertContains(respuesta, "ya estaba dado de baja")

    def test_el_practicante_dado_de_baja_no_puede_iniciar_sesion(self):
        self.client.post(self.url)
        self.client.logout()
        self.client.post(reverse("login"), {"username": "practicante1@prueba.com", "password": CLAVE})
        self.assertNotIn("_auth_user_id", self.client.session)


class ConsultaTests(TestCase):
    def setUp(self):
        self.client.force_login(crear_admin())
        self.url = reverse("practicantes:lista")

    def test_lista_vacia(self):
        self.assertContains(self.client.get(self.url), "No hay practicantes")

    def test_busqueda_por_nombre(self):
        crear_practicante(1)
        crear_practicante(2, matricula="X-999")
        respuesta = self.client.get(self.url, {"q": "practicante 02"})
        self.assertEqual([p.matricula for p in respuesta.context["practicantes"]], ["X-999"])

    def test_busqueda_por_matricula(self):
        crear_practicante(1)
        crear_practicante(2, matricula="X-999")
        respuesta = self.client.get(self.url, {"q": "x-999"})
        self.assertEqual(len(respuesta.context["practicantes"]), 1)

    def test_filtro_por_estado(self):
        crear_practicante(1)
        crear_practicante(2, estado=Practicante.Estado.TERMINADO)
        respuesta = self.client.get(self.url, {"estado": "terminado"})
        self.assertEqual([p.estado for p in respuesta.context["practicantes"]], ["terminado"])

    def test_estado_invalido_se_ignora(self):
        crear_practicante(1)
        respuesta = self.client.get(self.url, {"estado": "inventado"})
        self.assertEqual(len(respuesta.context["practicantes"]), 1)

    def test_paginacion_de_10_en_10(self):
        for numero in range(1, 13):
            crear_practicante(numero)
        pagina_1 = self.client.get(self.url)
        pagina_2 = self.client.get(self.url, {"page": 2})
        self.assertEqual(len(pagina_1.context["practicantes"]), 10)
        self.assertEqual(len(pagina_2.context["practicantes"]), 2)

    def test_la_paginacion_conserva_la_busqueda(self):
        for numero in range(1, 13):
            crear_practicante(numero)
        respuesta = self.client.get(self.url, {"q": "Practicante"})
        self.assertContains(respuesta, "?page=2&amp;q=Practicante")

    def test_ficha_del_practicante(self):
        practicante = crear_practicante(1)
        respuesta = self.client.get(reverse("practicantes:detalle", args=[practicante.pk]))
        self.assertContains(respuesta, "Practicante 01")
        self.assertContains(respuesta, "480 h")
        self.assertContains(respuesta, "M0001")

    def test_practicante_inexistente_da_404(self):
        self.assertEqual(self.client.get(reverse("practicantes:detalle", args=[999])).status_code, 404)


class DatosDeEjemploTests(TestCase):
    def test_el_comando_crea_los_datos_y_es_repetible(self):
        salida = StringIO()
        call_command("cargar_datos_ejemplo", stdout=salida)
        self.assertEqual(Practicante.objects.count(), 12)
        self.assertEqual(Usuario.objects.filter(rol=Usuario.Rol.ADMINISTRADOR).count(), 1)
        call_command("cargar_datos_ejemplo", stdout=salida)
        self.assertEqual(Practicante.objects.count(), 12)
        self.assertIn("ya existen", salida.getvalue())
