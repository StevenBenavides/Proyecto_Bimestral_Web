# Proyecto Bimestral Web - Giro Mayorista

Este proyecto corresponde a una aplicación web desarrollada en Django para apoyar la gestión de pedidos, clientes, vendedores, proveedores y trazabilidad en una empresa distribuidora mayorista. La plataforma permite registrar información clave del negocio y facilitar el seguimiento de operaciones relacionadas con la logística y la administración.

## Requisitos previos

Para poder desplegar y ejecutar este proyecto correctamente, se recomienda tener instalado lo siguiente:

- Python 3.10 o superior (se recomienda Python 3.11 o 3.12)
- pip actualizado
- Git
- Línea de comandos de Windows (CMD)

## Dependencias y tecnologías utilizadas

El proyecto funciona con las siguientes tecnologías y librerías:

- Python
- Django 5.2.10
- django-import-export 4.4.1
- SQLite, que viene incluido por defecto con Django

## Pasos de instalación y despliegue en Windows (CMD)

1. Abrir la terminal de comandos y dirigirse a la carpeta del proyecto:

   cd C:\ruta\al\proyecto\Proyecto_Bimestral_Web\giroMayorista

2. Crear un entorno virtual:

   py -m venv venv

3. Activar el entorno virtual:

   venv\Scripts\activate

4. Actualizar pip:

   python -m pip install --upgrade pip

5. Instalar las dependencias necesarias:

   pip install django==5.2.10 django-import-export==4.4.1

6. Aplicar las migraciones de la base de datos:

   python manage.py migrate

7. Crear un usuario administrador para acceder al panel de administración:

   python manage.py createsuperuser

8. Ejecutar el servidor de desarrollo:

   python manage.py runserver

9. Abrir el navegador en la siguiente URL:

   http://127.0.0.1:8000/

## Accesos recomendados

- Página principal: http://127.0.0.1:8000/
- Panel administrativo: http://127.0.0.1:8000/admin/



