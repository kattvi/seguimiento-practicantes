from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

Usuario = get_user_model()
CLAVE = "Cl4ve-de-prueba-2026"


class UsuarioTests(TestCase):
    def test_create_user_es_practicante_por_defecto(self):
        usuario = Usuario.objects.create_user(correo="a@prueba.com", password=CLAVE, nombre="A")
        self.assertEqual(usuario.rol, Usuario.Rol.PRACTICANTE)
        self.assertFalse(usuario.es_administrador)
        self.assertFalse(usuario.is_staff)

    def test_create_superuser_es_administrador(self):
        usuario = Usuario.objects.create_superuser(correo="b@prueba.com", password=CLAVE, nombre="B")
        self.assertTrue(usuario.es_administrador)
        self.assertTrue(usuario.is_staff)
        self.assertTrue(usuario.is_superuser)

    def test_la_contrasena_se_guarda_cifrada(self):
        usuario = Usuario.objects.create_user(correo="c@prueba.com", password=CLAVE, nombre="C")
        self.assertNotEqual(usuario.password, CLAVE)
        self.assertTrue(usuario.check_password(CLAVE))

    def test_el_correo_es_obligatorio(self):
        with self.assertRaises(ValueError):
            Usuario.objects.create_user(correo="", password=CLAVE, nombre="D")


class InicioSesionTests(TestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_user(
            correo="admin@prueba.com", password=CLAVE, nombre="Admin", rol=Usuario.Rol.ADMINISTRADOR
        )
        self.practicante = Usuario.objects.create_user(correo="p@prueba.com", password=CLAVE, nombre="Pract")

    def test_login_correcto_del_administrador_lleva_a_la_lista(self):
        respuesta = self.client.post(
            reverse("login"), {"username": "admin@prueba.com", "password": CLAVE}, follow=True
        )
        self.assertRedirects(respuesta, reverse("practicantes:lista"))

    def test_login_con_contrasena_incorrecta(self):
        respuesta = self.client.post(reverse("login"), {"username": "admin@prueba.com", "password": "otra"})
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_usuario_inactivo_no_puede_entrar(self):
        self.practicante.is_active = False
        self.practicante.save()
        self.client.post(reverse("login"), {"username": "p@prueba.com", "password": CLAVE})
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_inicio_sin_sesion_redirige_al_login(self):
        respuesta = self.client.get(reverse("inicio"))
        self.assertRedirects(respuesta, f"{reverse('login')}?next={reverse('inicio')}")

    def test_inicio_del_practicante_muestra_su_pagina(self):
        self.client.force_login(self.practicante)
        respuesta = self.client.get(reverse("inicio"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Tu cuenta de practicante está activa")

    def test_logout_cierra_la_sesion(self):
        self.client.force_login(self.admin)
        self.client.post(reverse("logout"))
        self.assertNotIn("_auth_user_id", self.client.session)
