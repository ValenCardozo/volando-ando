# Volando Ando

Este es un proyecto web desarrollado con Django.

## Instalación

Sigue estos pasos para configurar el entorno de desarrollo local.

### Prerrequisitos

- Python 3.x
- pip (manejador de paquetes de Python)

### Pasos

1.  **Clona el repositorio:**
    ```bash
    git clone <URL-DEL-REPOSITORIO>
    cd volando-ando
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    # Para macOS y Linux
    python3 -m venv .venv
    source .venv/bin/activate

    # Para Windows
    python -m venv .venv
    .venv\Scripts\activate
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install -r requeriments.txt
    ```

4.  **Aplica las migraciones de la base de datos:**
    ```bash
    cd fly_project
    python manage.py migrate
    ```

5.  **Inicia el servidor de desarrollo:**
    ```bash
    python manage.py runserver
    ```

6.  Abre tu navegador y ve a `http://127.0.0.1:8000/` para ver la aplicación en funcionamiento.

## Cargar datos de seed en la base de datos

Para que los demás integrantes puedan cargar los datos de ejemplo (seed) en la base de datos, simplemente ejecuten el siguiente comando desde la raíz del proyecto:

```bash
python3 fly_project/manage.py dbshell < fly_project/seeds/seed_arg_airline.sql
python3 fly_project/manage.py dbshell < fly_project/seeds/seed_destinations.sql
```

Esto insertará los datos del archivo `seeds/seed_arg_airline.sql` y `seed_destinations.sql` en la base de datos SQLite utilizada por el proyecto.
