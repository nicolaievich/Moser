# Moser

**Moser** es un monitor de servidores pequeño, ligero y educativo. Su objetivo es ofrecer una visión clara del estado de un servidor Linux, sin convertirse en un panel de administración complejo.

> **Panóptico del servidor:** ver qué está pasando, qué se está ejecutando y qué recursos está utilizando.

**Versión actual: 0.3.0**

## Instalación y uso

La instalación debe ser deliberadamente simple.

### Instalación nueva

```bash
git clone https://github.com/nicolaievich/Moser.git
cd Moser
./install.sh
```

El instalador:

- detecta Python 3;
- crea el entorno virtual `venv`;
- instala las dependencias;
- crea la configuración local y una clave de sesión segura;
- prepara el directorio de datos.

### Iniciar Moser

Después de instalar:

```bash
./start.sh
```

No hace falta activar manualmente el `venv`, entrar en `app/`, usar `python app/main.py`, recordar el comando de Uvicorn ni utilizar `sudo`.

Moser queda disponible en:

```
http://localhost:3000
```

Desde otra máquina de la red:

```
http://IP-DEL-SERVIDOR:3000
```

### Actualizar una instalación existente

```bash
git pull
./install.sh
./start.sh
```

El instalador reutiliza el `venv` existente y conserva la configuración local.

### Datos y configuración

Los datos se guardan en `data/moser.db`.

La configuración local se guarda en `.env`, que no forma parte del repositorio.

Para cambiar el directorio de datos puede utilizarse:

```bash
MOSER_DATA_DIR=/ruta/al/directorio
```

## Objetivo

Moser muestra en una única interfaz:

- CPU y carga del sistema.
- Memoria RAM.
- Almacenamiento.
- Red.
- Procesos.
- Contenedores Docker y su estado.
- Servicios seleccionados.
- Estado general del servidor.

La pantalla **Monitor** es el centro del proyecto: debe permitir saber rápidamente qué está pasando.

## Filosofía

Moser no pretende reemplazar herramientas como Cockpit, Webmin o Portainer.

Es un proyecto propio, pequeño y comprensible, pensado para aprender, monitorizar servidores de prueba, mantener el código sencillo y evitar permisos innecesarios.

**Principio de uso:** si para arrancar Moser hay que recordar una estructura interna de Python, estamos complicándolo demasiado.

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
        └── Monitor Docker ───────► Docker API

Moser observa el sistema. No inicia, detiene ni modifica servicios.

## Autenticación

En la primera ejecución Moser muestra `/setup` para crear el usuario inicial.

El registro solicita:

- usuario;
- contraseña;
- repetición de contraseña;
- indicador de complejidad;
- opción para mostrar la contraseña.

Las contraseñas se almacenan mediante Argon2id.

## Monitor

La pantalla principal muestra:

- información básica del hardware;
- CPU;
- RAM;
- disco;
- procesos;
- Docker;
- servicios;
- interfaces de red;
- estado general.

La información se actualiza automáticamente sin recargar toda la página.

## Seguridad

Moser está pensado para observar, no administrar.

No requiere `sudo` para arrancar. Si una consulta del sistema no puede realizarse con los permisos del usuario que ejecuta Moser, esa información debe aparecer como no disponible en lugar de intentar elevar privilegios.

Se contemplan:

- HTTPS mediante Cloudflare Tunnel;
- contraseñas con Argon2id;
- cookies de sesión;
- validación de entradas;
- secretos mediante variables de entorno;
- mínimo privilegio.

## Desarrollo

### 0.3.0 — Simplificación de instalación y ejecución

- Se incorpora `install.sh`.
- Se incorpora `start.sh`.
- El arranque deja de depender de activar manualmente el `venv`.
- El arranque funciona independientemente del directorio desde el que se invoque.
- Se genera automáticamente una clave de sesión local.
- Se documenta el flujo de instalación y actualización.
- Se muestra la versión en la interfaz.

### Próximos pasos

- Mejorar el monitoreo de servicios.
- Docker.
- Red.
- Histórico.
- Alertas.
- Configuración.

## Estructura

    Moser/
    ├── app/
    │   ├── main.py
    │   ├── auth.py
    │   └── monitoring/
    ├── templates/
    ├── static/
    ├── tests/
    ├── data/
    ├── venv/              # generado localmente
    ├── install.sh
    ├── start.sh
    ├── requirements.txt
    └── README.md

La complejidad se agrega solamente cuando aporta una función concreta.

## Estado

**Pre-alpha — autenticación inicial + monitor funcional.**

La versión 0.3.0 pone el foco en algo fundamental: **Moser debe ser tan fácil de instalar y ejecutar como cualquier herramienta que realmente queramos usar.**
