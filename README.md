# Sistema web para el control y seguimiento de practicantes

Proyecto de prácticas profesionales para el Centro de Talentos. Sirve para registrar practicantes,
sus actividades y horas, calcular su avance y generar el reporte de horas en PDF.

Estado: el módulo de practicantes (alta, edición, baja y consulta) está desarrollado.
Siguen el registro de actividades y horas, y los reportes en PDF.

## Contenido del repositorio

- `config/`: configuración del proyecto Django.
- `cuentas/`: usuarios con rol (administrador o practicante) e inicio de sesión.
- `practicantes/`: módulo de practicantes.
- `templates/`: plantilla base y página de "sin permiso".
- `database/schema.sql`: diseño de la base de datos en SQL. Es una referencia: las tablas del sistema
  se crean con las migraciones de Django, que además agregan algunas columnas y tablas propias.
- `docs/requerimientos/`: documento de requerimientos.
- `docs/base-de-datos/`: diseño de la base de datos, con su diagrama.
- `docs/arquitectura/`: arquitectura del sistema, con su diagrama.

## Qué hace el módulo de practicantes

| Requerimiento | Función |
|---|---|
| RF-01 y RF-02 | Inicio y cierre de sesión con correo y contraseña; solo el administrador entra al módulo |
| RF-03 | Alta de un practicante junto con su cuenta de usuario |
| RF-04 | Edición de los datos del practicante |
| RF-05 | Baja lógica: cambia el estado y desactiva la cuenta, sin borrar el historial |
| RF-06 | Lista con búsqueda por nombre o matrícula, filtro por estado y paginación |

## Preparar el entorno

Se necesita Python 3.11 o superior, MySQL 8.0.16 o superior y Git.

```bash
git clone <url-del-repositorio>
cd seguimiento-practicantes

python3 -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Crea la base de datos vacía (las tablas las crea Django):

```bash
mysql -u root -p -e "CREATE DATABASE seguimiento_practicantes CHARACTER SET utf8mb4;"
```

## Ejecutar el sistema

La conexión a MySQL se configura con variables de entorno. Si no las defines, se usan estos valores:
`DB_NAME=seguimiento_practicantes`, `DB_USER=root`, `DB_PASSWORD` vacía, `DB_HOST=127.0.0.1` y `DB_PORT=3306`.

```bash
export DB_PASSWORD="la-contraseña-de-tu-mysql"
python manage.py migrate
python manage.py createsuperuser      # pide correo, nombre y contraseña; crea un administrador
python manage.py runserver
```

Abre http://127.0.0.1:8000/ e inicia sesión con el administrador que creaste.

Para probar con datos de ejemplo (solo en tu computadora, nunca en un sistema real):

```bash
python manage.py cargar_datos_ejemplo
```

El comando crea un administrador y 12 practicantes ficticios, y muestra en pantalla los datos de acceso.

## Pruebas

Las pruebas se pueden ejecutar sin MySQL usando SQLite:

```bash
DB_ENGINE=sqlite python manage.py test
```

## Flujo de ramas

| Rama | Para qué se usa |
|---|---|
| `main` | Versión estable. Solo recibe cambios desde `develop`. |
| `develop` | Aquí se juntan los cambios terminados. |
| `feature/<nombre>` | Una tarea o módulo. Se crea desde `develop` y regresa a `develop`. |

Reglas: no se hacen commits directos en `main` ni en `develop`, y las ramas `feature/*`
se unen con `git merge --no-ff` para conservar el historial.

Los mensajes de commit llevan un tipo y una descripción corta, por ejemplo
`feat: agregar alta de practicantes` o `docs: actualizar requerimientos`.
Tipos: `feat` (funcionalidad), `fix` (error), `docs` (documentación), `test` (pruebas)
y `chore` (configuración).
