# Moser

**Moser** es un monitor de servidores pequeño, ligero y educativo. Su objetivo es ofrecer una visión clara del estado de un servidor Linux, sin convertirse en un panel de administración complejo.

> **Panóptico del servidor:** ver qué está pasando, qué se está ejecutando y qué recursos está utilizando.

**Versión actual: 0.4.0**

## Instalación y uso

Moser ofrece dos modos de uso: desarrollo manual y servicio permanente. En ambos, la aplicación se ejecuta sin privilegios de administrador.

### Desarrollo o prueba manual

Cloná el repositorio y ejecutá estos comandos como tu usuario normal, sin sudo:

    git clone https://github.com/nicolaievich/Moser.git
    cd Moser
    ./install.sh
    ./start.sh

El instalador prepara el entorno virtual de Python, instala dependencias, genera una clave de sesión y protege la configuración y el directorio de datos. Por defecto, Moser escucha solamente en 127.0.0.1:3000.

Si falta Python o el módulo venv, instalá los paquetes del sistema por separado:

    sudo apt install python3 python3-venv

No ejecutes install.sh ni start.sh con sudo. Si un archivo quedó accidentalmente en propiedad de root, el instalador muestra cómo diagnosticarlo sin borrar la base de datos.

### Servicio permanente (recomendado para servidores)

Para una instalación permanente, ubicá el repositorio en una ruta estable bajo /opt o /srv. Desde esa carpeta, primero instalá las dependencias como usuario normal y luego configurá el servicio:

    ./install.sh
    sudo ./install-service.sh

El instalador de servicio usa sudo solamente para crear el usuario Linux exclusivo moser, preparar directorios privados y registrar una unidad de systemd. La aplicación se ejecuta como moser, no como root.

El servicio:
- escucha únicamente en 127.0.0.1:3000;
- almacena la base de datos en /var/lib/moser;
- guarda la configuración privada en /etc/moser/moser.env;
- no recibe capacidades Linux adicionales;
- tiene el sistema de archivos protegido contra escritura salvo el directorio de datos;
- no se agrega automáticamente al grupo docker, porque ese acceso puede equivaler a privilegios de administrador.

Si ya tenías una base de datos en data/moser.db, el instalador la copia a /var/lib/moser/moser.db cuando todavía no existe una base de datos del servicio. No reemplaza una base de datos existente.

Comandos útiles:

    sudo systemctl status moser
    sudo journalctl -u moser -n 50 --no-pager
    sudo systemctl restart moser
    sudo systemctl stop moser

No arranques ./start.sh mientras el servicio esté activo.

## Manual de seguridad

Leé **[Manual de instalación, permisos y seguridad](docs/SEGURIDAD.md)** para conocer:
- por qué la instalación y la ejecución usan permisos diferentes;
- dónde se guardan el código, la configuración y los datos;
- cómo funciona el usuario de servicio;
- cómo configurar el acceso remoto y HTTPS;
- por qué el acceso a Docker es opcional y sensible;
- cómo actualizar y diagnosticar errores de permisos de SQLite.

## Objetivo

Moser muestra en una única interfaz:

- CPU y carga del sistema.
- Memoria RAM.
- Almacenamiento.
- Red.
- Procesos.
- Contenedores Docker y su estado, si el proceso tiene permisos para consultarlos.
- Servicios seleccionados.
- Estado general del servidor.

La pantalla **Monitor** es el centro del proyecto: debe permitir saber rápidamente qué está pasando.

## Filosofía

Moser no pretende reemplazar herramientas como Cockpit, Webmin o Portainer.

Es un proyecto propio, pequeño y comprensible, pensado para aprender, monitorizar servidores de prueba, mantener el código sencillo y evitar permisos innecesarios.

**Principios:** mínimo privilegio, instalación clara, datos persistentes separados del código y errores de permisos detectados temprano.

## Stack

### Backend
- Python
- FastAPI
- Uvicorn
- psutil
- Docker SDK para Python
- SQLite
- Argon2id
- Cookies de sesión

### Frontend
- HTML
- CSS
- JavaScript
- Jinja2

No se utiliza inicialmente un framework frontend pesado.

## Arquitectura

    Navegador
        │
        │ HTTP/HTTPS
        ▼
    FastAPI / Uvicorn
        │
        ├── Autenticación
        ├── API
        ├── Monitor del sistema ──► psutil
        └── Monitor Docker ───────► Docker API (opcional)

Moser observa el sistema. No inicia, detiene ni modifica servicios.

## Autenticación

En la primera ejecución Moser muestra /setup para crear el usuario inicial. Una vez creada una cuenta, el acceso debe pasar por el inicio de sesión. Las contraseñas se almacenan mediante Argon2id.

La clave de sesión se genera durante la instalación y se guarda en un archivo local que no se sube al repositorio. En el arranque se verifica que exista una clave; si falta, Moser falla con un mensaje explícito en lugar de utilizar una clave insegura por defecto.

## Seguridad

- No se ejecuta Moser como root.
- El modo manual escucha en localhost por defecto.
- La configuración y los datos tienen permisos privados.
- La aplicación comprueba al iniciar que SQLite sea escribible; si no, informa el problema en los registros en vez de mostrar un ciclo de registro con errores 500.
- El servicio permanente usa un usuario Linux exclusivo y una unidad de systemd endurecida.
- El acceso a Docker no se habilita automáticamente.
- HTTPS y el control de acceso remoto deben configurarse conscientemente.

Estas medidas reducen riesgos, pero no sustituyen una revisión completa antes de exponer la aplicación a usuarios externos. Moser sigue siendo un proyecto educativo en desarrollo.

## Desarrollo

### 0.4.0 — Instalación segura y permisos coherentes

- Se documentan los modos de desarrollo y servicio permanente.
- Se incorpora instalación opcional con usuario exclusivo moser y systemd.
- Se separan código, configuración privada y datos del servicio.
- Se restringe el acceso de red a localhost por defecto.
- Se evita ejecutar los scripts de desarrollo como root.
- Se comprueban los permisos de SQLite al iniciar.
- Se corrigen los permisos privados de configuración y datos.
- Se documenta el riesgo de conceder acceso al socket de Docker.
- Se actualizan la versión y las instrucciones de operación.

### Próximos pasos

- Mejorar el monitoreo de servicios.
- Histórico.
- Alertas.
- Configuración.
- Revisar protecciones adicionales de autenticación y acceso web.

## Estructura

    Moser/
    ├── app/
    │   ├── main.py
    │   ├── auth.py
    │   └── monitoring/
    ├── templates/
    ├── static/
    ├── tests/
    ├── docs/
    │   └── SEGURIDAD.md
    ├── deploy/
    │   └── moser.service.in
    ├── data/                 # datos de desarrollo local
    ├── venv/                 # generado localmente
    ├── install.sh
    ├── install-service.sh
    ├── start.sh
    ├── requirements.txt
    └── README.md

La complejidad se agrega solamente cuando aporta una función concreta.

## Estado

**Pre-alpha — autenticación inicial + monitor funcional.**

La versión 0.4.0 pone el foco en una base importante: Moser debe ser fácil de instalar y ejecutar, y sus permisos deben estar definidos para que los errores de propiedad de archivos no vuelvan a romper el registro de usuarios.
