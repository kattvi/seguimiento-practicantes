# Sistema web para el control y seguimiento de practicantes

Proyecto de prácticas profesionales para el Centro de Talentos. Sirve para registrar
practicantes, sus actividades y horas, calcular su avance y generar el reporte de horas en PDF.

Estado: análisis y diseño.

## Contenido del repositorio

- `database/schema.sql`: script que crea las tablas y la vista en MySQL.
- `docs/requerimientos/`: documento de requerimientos.
- `docs/base-de-datos/`: diseño de la base de datos, con su diagrama.
- `docs/arquitectura/`: arquitectura del sistema, con su diagrama.

## Preparar el entorno

Se necesita Python 3.11 o superior, MySQL 8.0.16 o superior y Git.

```bash
git clone <url-del-repositorio>
cd seguimiento-practicantes

python3 -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt

mysql -u root -p -e "CREATE DATABASE seguimiento_practicantes CHARACTER SET utf8mb4;"
mysql -u root -p seguimiento_practicantes < database/schema.sql
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
