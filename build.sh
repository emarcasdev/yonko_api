#!/bin/bash

# Instalar dependencias de Python
pip install -r requirements.txt

# Iniciar Gunicorn con el archivo de tu aplicación
gunicorn -w 4 -b 0.0.0.0:5000 api.index:app
