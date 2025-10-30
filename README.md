# Volando Ando

Este es un proyecto web desarrollado con Django.

## Instalación y arranque rápido

Sigue estos pasos para configurar y levantar el entorno de desarrollo local de forma automática:

### Prerrequisitos

- Python 3.x
- pip (manejador de paquetes de Python)
- fish o bash (shell compatible)

### Pasos rápidos

1. **Clona el repositorio:**
    ```bash
    git clone <URL-DEL-REPOSITORIO>
    cd volando-ando
    ```

2. **Ejecuta el setup automático:**
    ```bash
    ./setup.sh
    ```
    Esto instalará dependencias, aplicará migraciones y cargará los seeders.

3. **Levanta el servidor:**
    ```bash
    ./runserver.sh
    ```
    El servidor estará disponible en `http://127.0.0.1:8000/`

---

## Proceso manual (opcional)

Si prefieres hacerlo manualmente:

1.  **Crea y activa un entorno virtual:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # o source .venv/bin/activate.fish si usas fish
    ```

2.  **Instala las dependencias:**
    ```bash
    pip install -r requeriments.txt
    ```

3.  **Aplica las migraciones de la base de datos:**
    ```bash
    cd fly_project
    python manage.py migrate
    ```

4.  **Carga los datos de seed en la base de datos:**
    ```bash
    python manage.py dbshell < seeds/seed_arg_airline.sql
    python manage.py dbshell < seeds/seed_destinations.sql
    cd ..
    ```

5.  **Inicia el servidor de desarrollo:**
    ```bash
    cd fly_project
    python manage.py runserver
    ```

---

## Ejecutar todos los tests

Para correr tanto los tests unitarios como los de integración de forma automática, ejecuta:

```bash
./run_tests.sh
```

Esto ejecutará todos los tests definidos en el proyecto y mostrará un resumen de los resultados.

---

## Notas
- Los scripts `setup.sh` y `runserver.sh` detectan automáticamente si usas fish o bash.
- Recuerda dar permisos de ejecución a los scripts si es necesario:
    ```bash
    chmod +x setup.sh runserver.sh
    ```
