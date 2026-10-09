# Seguridad e instalación de Moser

Este documento explica cómo instalar, ejecutar y mantener Moser sin conceder permisos innecesarios. Está pensado para Ubuntu/Debian con systemd.

## 1. La regla principal

**Instalar y ejecutar son tareas diferentes.** Algunos cambios del sistema requieren sudo; el proceso web de Moser no.

Moser es un monitor: lee métricas y estados. No necesita privilegios de administrador para arrancar. Si una fuente de información no está disponible con los permisos actuales, debe informar que no está disponible, no elevar privilegios por su cuenta.

Aplicamos el principio de mínimo privilegio: cada usuario y proceso recibe solamente los permisos que necesita.

## 2. Dos modos de uso

### Desarrollo o prueba manual

Para probar cambios desde el repositorio:

    ./install.sh
    ./start.sh

Ambos comandos se ejecutan como tu usuario normal. El instalador prepara un entorno virtual de Python, crea una configuración local y protege el directorio de datos. Moser escucha en 127.0.0.1:3000 por defecto, por lo que solo acepta conexiones locales.

No uses sudo ./install.sh ni sudo ./start.sh. Ejecutar el instalador como root puede dejar archivos propiedad de root; ejecutar la aplicación como root aumenta el impacto de una posible vulnerabilidad.

Si necesitás instalar paquetes del sistema, hacelo por separado y con un comando explícito, por ejemplo:

    sudo apt install python3 python3-venv

### Servicio permanente

En un servidor, el modo recomendado es un servicio de systemd bajo un usuario exclusivo llamado moser.

Desde una instalación estable situada en /opt o /srv:

    ./install.sh
    sudo ./install-service.sh

El primer comando se ejecuta como tu usuario. El segundo requiere privilegios administrativos únicamente para crear el usuario de servicio, configurar directorios privados y registrar el servicio en systemd.

El servicio se ejecuta como moser, con shell de inicio deshabilitada, sin capacidades Linux adicionales y con el sistema de archivos protegido contra escritura salvo el directorio de datos.

Comandos útiles:

    sudo systemctl status moser
    sudo journalctl -u moser -n 50 --no-pager
    sudo systemctl restart moser
    sudo systemctl stop moser

No arranques una segunda copia con ./start.sh mientras el servicio está activo.

## 3. Dónde se guardan los archivos

| Recurso | Modo de desarrollo | Servicio permanente |
|---|---|---|
| Código y entorno virtual | Copia del repositorio | Código legible, no modificable por el usuario moser |
| Configuración y secreto de sesión | .env, accesible solo por el usuario de desarrollo | /etc/moser/moser.env, root:moser, permisos 0640 |
| Base de datos SQLite | data/moser.db | /var/lib/moser/moser.db |
| Propietario de los datos | Usuario que ejecuta Moser | Usuario y grupo moser |
| Dirección de escucha | 127.0.0.1:3000 por defecto | 127.0.0.1:3000 |

El directorio de datos debe permitir al proceso crear y modificar la base de datos. SQLite también necesita acceso de escritura al directorio para determinadas operaciones y archivos auxiliares. No alcanza con que el archivo exista o sea legible.

Los datos de la aplicación no deben pertenecer a root si el proceso que los utiliza no se ejecuta como root. No soluciones un error de SQLite ejecutando toda la aplicación con sudo.

El instalador del servicio copia la base de datos de desarrollo a /var/lib/moser/moser.db si allí todavía no existe una base de datos. No sobrescribe una base de datos que ya exista en el directorio del servicio.

## 4. ¿Por qué puede usarse sudo durante la instalación?

Usamos privilegios administrativos solamente para acciones del sistema operativo, como:

- instalar paquetes del sistema con APT;
- crear el usuario y grupo de sistema moser;
- crear directorios protegidos en /var/lib y /etc;
- instalar y habilitar la unidad de systemd.

No se usan para instalar dependencias dentro del entorno virtual ni para ejecutar el servidor web.

## 5. Red, HTTPS y acceso remoto

Moser escucha en 127.0.0.1 por defecto. El servicio de systemd también fija esa dirección deliberadamente. Esto permite colocarlo detrás de un proxy inverso o Cloudflare Tunnel sin exponer directamente el puerto 3000 a la red.

No publiques el puerto 3000 ni cambies la dirección a 0.0.0.0 sin entender las reglas de firewall, la autenticación y el cifrado del acceso. Para desarrollo en una LAN, configurá conscientemente MOSER_HOST en el archivo .env; no es el valor recomendado para un servidor expuesto.

En modo servicio, MOSER_COOKIE_SECURE=true indica al navegador que solo envíe la cookie de sesión por HTTPS. Si se accede por HTTP directo, el inicio de sesión puede no funcionar; usá HTTPS o una configuración local de desarrollo separada.

SSH, Cloudflare Access y el inicio de sesión de Moser son controles distintos. Tener acceso SSH no autoriza automáticamente a otras personas a utilizar Moser.

## 6. Docker: permiso opcional y sensible

Moser puede consultar Docker mediante su SDK, pero el acceso depende de los permisos del sistema. El socket de Docker puede permitir controlar contenedores y, en muchas configuraciones, obtener control equivalente a root sobre el host.

Por ese motivo, el instalador **no agrega automáticamente** al usuario moser al grupo docker. Si Docker aparece como no disponible, el monitor puede seguir funcionando. Evaluá el riesgo antes de habilitar ese acceso; no lo resuelvas ejecutando Moser como root.

## 7. Primer usuario y autenticación

La primera visita muestra la configuración inicial solamente mientras no exista un usuario en la base de datos. Después de crear el primer usuario, la ruta de configuración debe redirigir al inicio de sesión.

Las contraseñas se almacenan con Argon2id. La clave de sesión se genera durante la instalación y no debe compartirse ni subirse al repositorio. Los archivos .env y moser.env contienen configuración privada y deben mantenerse fuera de Git.

Si Moser no puede escribir en SQLite, el servicio debe fallar al iniciar y dejar un mensaje claro en los registros, en vez de aparentar que no existe ningún usuario y repetir el formulario de registro.

## 8. Actualizar el código

Antes de actualizar, hacé una copia de seguridad de la base de datos y detené el servicio:

    sudo systemctl stop moser

Actualizá el repositorio como el usuario propietario del código; no hagas git pull con sudo. Luego instalá dependencias como usuario normal:

    git pull
    ./install.sh

Y reiniciá el servicio:

    sudo systemctl start moser
    sudo systemctl status moser

El directorio de datos del servicio está separado del repositorio, por lo que una actualización de código no debería reemplazar la base de datos ni los secretos.

## 9. Diagnóstico de permisos

Si la aplicación no arranca:

    sudo systemctl status moser
    sudo journalctl -u moser -n 80 --no-pager
    ls -ld /var/lib/moser
    ls -l /var/lib/moser/moser.db
    sudo systemctl show moser -p User -p Group -p ReadWritePaths

El usuario de servicio debe poder escribir en /var/lib/moser; no necesita permisos de escritura sobre el código.

En modo desarrollo:

    ls -ld data
    ls -l data/moser.db

Si los archivos de desarrollo quedaron accidentalmente en propiedad de root, detené Moser y corregí solamente la carpeta de datos, verificando primero la ruta. Por ejemplo:

    sudo chown -R "$USER":"$(id -gn)" ./data

No borres moser.db como método de diagnóstico: contiene las cuentas de usuario.

## 10. Límites y revisión

Estas medidas reducen el impacto de errores, pero no convierten por sí solas una aplicación en segura para Internet. Antes de exponer Moser a usuarios externos, revisá la autenticación, protección contra CSRF, límites de intentos, actualizaciones de dependencias, copias de seguridad y configuración del proxy.

Moser es un proyecto educativo en desarrollo. Mantené el acceso restringido a usuarios de confianza hasta completar esas revisiones.
