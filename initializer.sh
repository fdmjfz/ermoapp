#!/bin/bash

if [ ! -d ./ermovenv ]
then 
    echo "Non existe entorno virtual. Creando un novo."
    #sudo apt update
    sudo apt install -y python3-pip
    sudo apt-get install -y python3-venv
    python3 -m venv ./ermovenv
    source ./ermovenv/bin/activate
    
    echo "Instalando as librerias necesarias."
    python3 -m pip install --upgrade pip
    pip uninstall serial
    pip install -r requirements.txt
    
else
    echo "Atopado entorno virtual."
    source ./ermovenv/bin/activate
fi

python3 pruebas.py
deactivate