# Moser

**Moser** es un monitor de servidores pequeño, ligero y educativo. Su objetivo es ofrecer una visión clara del estado de un servidor Linux y de los servicios que ejecuta, sin intentar convertirse en un panel de administración completo.

> **Panóptico del servidor:** ver qué está pasando, qué se está ejecutando y qué recursos está utilizando.

## Objetivo

Moser mostrará en una única interfaz:
- CPU y carga del sistema.
- Memoria RAM.
- Almacenamiento.
- Red y actividad.
- Procesos relevantes.
- Contenedores Docker y su estado.
- Puertos abiertos y servicios detectados.
- Servicios seleccionados para monitoreo.
- Información sobre conexiones y usuarios cuando pueda obtenerse de forma segura.
- Estado general del servidor.

La **pantalla Monitor** será el centro del proyecto: la parte que queremos tener abierta y consultar de un vistazo.

## Filosofía

Moser no pretende reemplazar a herramientas como Cockpit, Webmin o Portainer.

Es un proyecto propio, pequeño y comprensible, pensado para aprender, monitorizar nuestro servidor de pruebas, mantener el código sencillo, evitar permisos innecesarios y ampliar el sistema progresivamente.

## Stack

### Backend
- **Python**
- **FastAPI** — framework web y API.
- **Uvicorn** — servidor ASGI.
- **psutil** — CPU, RAM, disco, red y procesos.
- **Docker SDK para Python** — consulta de contenedores Docker.
- **SQLite** — usuarios y configuración.
- **Argon2id** — almacenamiento seguro de contraseñas.
- Cookies de sesión seguras.
- **Authlib** como posible componente para OAuth en una etapa posterior.

### Frontend
- HTML.
- CSS.
- JavaScript.
- Jinja2 para plantillas cuando corresponda.

No se utilizará inicialmente un framework frontend pesado. La interfaz debe ser rápida, sencilla y fácil de mantener.

## Arquitectura

    Navegador
        │
        │ HTTPS
        ▼
    FastAPI / Uvicorn
        │
        ├── Autenticación
        ├── API
        ├── Monitor del sistema ──► psutil
        └── Monitor Docker ───────► Docker API
                 │
                 ▼
                Linux

El navegador nunca debería acceder directamente al sistema operativo ni a Docker. FastAPI funciona como intermediario.

## Autenticación

Flujo previsto:
1. Registro.
2. Confirmación de email pendiente.
3. Confirmación mediante enlace enviado por correo.
4. Login.
5. Recuperación de contraseña.
6. Email con enlace de recuperación.
7. Restablecimiento de contraseña.
8. Acceso al monitor.
9. Configuración protegida.

Las contraseñas no se almacenarán en texto plano. Se utilizará Argon2id.

En la primera ejecución, Moser muestra `/setup` para crear el usuario inicial. El registro solicita usuario, contraseña y confirmación; muestra la complejidad de la contraseña y permite verla mientras se escribe. Una vez creado, el monitor queda protegido por sesión. La base SQLite se guarda fuera del código mediante `MOSER_DATA_DIR` cuando se configura; por defecto se utiliza `data/moser.db`.

## Pantallas

### Registro
Formulario para crear la cuenta.

### Confirmación de email
Pantalla que informa que la cuenta está pendiente de verificar y permite continuar mediante el enlace enviado por correo.

### Login
Acceso mediante credenciales.

### Recuperación de contraseña
El usuario introduce su email y recibe un enlace temporal para restablecer la contraseña.

### Restablecer contraseña
Formulario para establecer una nueva contraseña utilizando el enlace recibido.

### Configuración
Permitirá elegir qué servicios queremos monitorizar.

La lista contemplará hasta 20 servicios populares, por ejemplo:
- Docker
- SSH
- Apache
- Nginx
- Caddy
- MySQL
- MariaDB
- PostgreSQL
- Redis
- PHP-FPM
- Node.js
- Python
- Samba
- Cron
- systemd
- Cloudflared
- n8n
- WordPress
- Fail2ban
- UFW

La mayoría aparecerán inicialmente como **Próximamente**. La versión 1.0 implementará primero los servicios y componentes presentes en nuestro entorno.

### Monitor
La pantalla principal de Moser.

Debe permitir saber rápidamente:
- ¿Está bien el servidor?
- ¿Cuánta CPU está utilizando?
- ¿Cuánta RAM queda?
- ¿Cuánto almacenamiento queda?
- ¿Qué procesos consumen recursos?
- ¿Qué contenedores están funcionando?
- ¿Qué servicios están disponibles?
- ¿Qué puertos están abiertos?
- ¿Qué conexiones existen?
- ¿Hay algo detenido o inesperado?

La información se actualizará periódicamente sin recargar toda la página.

## Frecuencia de actualización

- CPU/RAM: aproximadamente cada 2 segundos.
- Docker: aproximadamente cada 5 segundos.
- Puertos y servicios: aproximadamente cada 10 segundos.
- Procesos: según necesidad.
- Históricos: posteriormente, con intervalos mayores.

Los valores serán configurables si resulta necesario.

## Seguridad

Moser está pensado para observar, no administrar.

Una decisión importante es **no entregar inicialmente el socket /var/run/docker.sock a un contenedor Moser**, porque hacerlo concede capacidades muy sensibles sobre Docker y potencialmente sobre el host.

Durante la primera versión se priorizará ejecutar Moser directamente en el servidor como servicio, con permisos controlados.

Se contemplan:
- HTTPS mediante Cloudflare Tunnel.
- Contraseñas con Argon2id.
- Cookies seguras.
- Protección CSRF cuando corresponda.
- Rate limiting.
- Validación de entradas.
- Secretos mediante variables de entorno.
- Logs de acceso.
- Mínimo privilegio.
- No exponer información sensible innecesariamente.

## Estructura prevista

No se comenzará con una estructura gigantesca. Se agregará complejidad solamente cuando sea necesaria.

    Moser/
    ├── app/
    │   ├── main.py
    │   ├── config.py
    │   ├── auth/
    │   ├── monitoring/
    │   │   ├── system.py
    │   │   ├── docker.py
    │   │   ├── network.py
    │   │   └── processes.py
    │   ├── routes/
    │   └── database/
    ├── templates/
    ├── static/
    ├── tests/
    ├── .env
    ├── requirements.txt
    └── README.md

Cada módulo tendrá una responsabilidad concreta y el código estará ampliamente comentado para que el proyecto también funcione como material de aprendizaje.

## Desarrollo por etapas

### 0. Base
- Entorno virtual.
- FastAPI.
- Uvicorn.
- Primera ruta.
- Configuración básica.
- README.

### 1. Autenticación
- Base de datos.
- Configuración inicial del primer usuario.
- Login y cierre de sesión.
- Protección de la interfaz y API.
- Contraseñas con Argon2id.

- Registro.
- Confirmación de email.
- Login.
- Recuperación de contraseña.
- Restablecimiento.
- Sesiones seguras.

### 2. Monitor del sistema
- CPU.
- RAM.
- Disco.
- Red.
- Uptime.
- Procesos.

### 3. Docker
- Contenedores.
- Estado.
- Imágenes.
- Puertos.
- Consumo de recursos cuando esté disponible.

### 4. Servicios
- Detección.
- Estado.
- Configuración de servicios a monitorear.
- Primer conjunto de servicios soportados.

### 5. Red
- Puertos abiertos.
- Conexiones.
- Clientes conectados cuando la información pueda obtenerse de forma fiable.

### 6. Histórico
- Registro periódico de métricas.
- Gráficos.
- Tendencias.

### 7. Alertas
- Servicio caído.
- Uso elevado de CPU/RAM.
- Disco lleno.
- Contenedor detenido.
- Otros eventos relevantes.

## Rendimiento

Moser debe consumir pocos recursos. No se realizarán consultas agresivas ni se ejecutarán procesos innecesariamente cada segundo. Se utilizarán intervalos, caché cuando convenga y consultas específicas.

El objetivo es que el monitor consuma una fracción pequeña de los recursos del servidor que está observando.

## Mantenimiento

Principios:
- Código claro antes que código sofisticado.
- Dependencias justificadas.
- Una responsabilidad por módulo.
- Configuración separada del código.
- Variables sensibles fuera del repositorio.
- Tests para las partes críticas.
- Documentación actualizada.
- Cambios pequeños y comprobables.

## Estado del proyecto

**Pre-alpha — autenticación inicial + monitor funcional.**

La versión **1.0** priorizará:

> **Autenticación segura + monitor del servidor + Docker + servicios del entorno actual.**

Después se incorporarán nuevos servicios y funciones progresivamente.

## Nombre

**Moser** es el nombre del proyecto.

La idea es construir un pequeño **panóptico del servidor**: observar el estado de todo el sistema desde un único lugar, sin convertir esa observación en una administración innecesariamente compleja.