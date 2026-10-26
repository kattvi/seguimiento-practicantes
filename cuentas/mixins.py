from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class AdministradorRequeridoMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Solo deja pasar a usuarios con rol administrador.

    Sin sesión envía al inicio de sesión; con sesión pero sin permiso responde 403.
    """

    def test_func(self):
        return self.request.user.es_administrador
