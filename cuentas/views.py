from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


@login_required
def inicio(request):
    if request.user.es_administrador:
        return redirect("practicantes:lista")
    return render(request, "cuentas/inicio_practicante.html")
