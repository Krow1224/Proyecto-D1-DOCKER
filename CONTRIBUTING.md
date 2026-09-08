# 🚀 Guía de Colaboración y Flujo de Trabajo en Git

¡Bienvenido al proyecto! Para mantener la arquitectura del sistema funcional y evitar conflictos de código o problemas con los archivos de entorno (Docker, Redis, PostgreSQL), seguiremos un flujo de trabajo estándar basado en **Forks y Pull Requests**.

---

## 📄 Índice
1. Configuración Inicial (Fork & Clon)
2. Configuración del Entorno de Desarrollo (Crucial para Windows/Docker)
3. Flujo Diario de Trabajo (Branches)
4. Creación de un Pull Request (PR)
5. Cómo Sincronizar tu Proyecto con la Rama Principal

---

## 1. Configuración Inicial

### Paso 1: Crear un Fork
1. Entra al repositorio principal en GitHub.
2. Haz clic en el botón **Fork** (arriba a la derecha).
3. Esto creará una copia idéntica del repositorio en tu propia cuenta de GitHub.

### Paso 2: Clonar TU Fork en tu máquina
Abre tu terminal en la carpeta donde guardas tus proyectos y ejecuta:

```bash
git clone https://github.com/TU_USUARIO/NOMBRE_DEL_REPOSITO.git
cd NOMBRE_DEL_REPOSITO
```

### Paso 3: Configurar el remoto original (`upstream`)
Para poder descargar las actualizaciones que otros vayan subiendo al proyecto principal, debemos vincular el repositorio original como `upstream`:

```bash
git remote add upstream https://github.com/USUARIO_PROPIETARIO/NOMBRE_DEL_REPOSITO.git
```

Verifica tus remotos ejecutando `git remote -v`. Deberías ver:
* `origin`: Tu fork personal.
* `upstream`: El repositorio principal del equipo.

---

## 2. Configuración del Entorno (Sistemas en Windows)

Para evitar que Windows modifique la codificación de los archivos de texto (`LF` vs `CRLF`) y rompa la ejecución de los scripts de Linux y configuraciones dentro de los contenedores Docker, configura Git **únicamente para este proyecto**:

```bash
git config core.autocrlf input
```

---

## 3. Flujo Diario de Trabajo

> ⚠️ **REGLA DE ORO**: Nunca trabajes ni hagas commits directamente sobre la rama `main`. Usa siempre ramas descriptivas para cada tarea.

### Paso 1: Crear una rama para tu tarea
Antes de escribir cualquier línea de código, crea una rama específica:

```bash
# Cambiar a main y asegurarte de estar actualizado
git checkout main
git pull upstream main

# Crear y cambiar a tu nueva rama
git checkout -b feature/nombre-de-tu-tarea
```
*Ejemplos de nombres de ramas*: `feature/login-jwt`, `fix/redis-connection-error`, `refactor/cart-service`.

### Paso 2: Guardar y commitear tus cambios
A medida que avances en tu código:

```bash
# 1. Ver qué archivos modificaste
git status

# 2. Agregar los archivos al área de staging
git add .

# 3. Guardar los cambios con un mensaje claro y descriptivo
git commit -m "feat: agrega validacion de stock en el servicio de checkout"
```

---

## 4. Subir Cambios y Crear un Pull Request (PR)

Cuando termines tu tarea y hayas probado que los contenedores de Docker levantan correctamente (`docker compose up -d`):

### Paso 1: Subir la rama a TU Fork (`origin`)
```bash
git push -u origin feature/nombre-de-tu-tarea
```

### Paso 2: Crear el Pull Request en GitHub
1. Ve a tu fork en GitHub.
2. Verás un banner amarillo que dice **"Compare & pull request"**. Haz clic en él.
3. Escribe un título descriptivo y explica brevemente los cambios realizados.
4. Envía el Pull Request para que sea revisado y fusionado a la rama `main` del proyecto principal.

---

## 5. Cómo Sincronizar tu Proyecto (Evitar Conflictos)

Si otros miembros del equipo han subido cambios al repositorio principal (`upstream`) mientras tú trabajabas, debes actualizar tu código local antes de continuar o enviar un PR:

```bash
# 1. Cambiar a tu rama main local
git checkout main

# 2. Descargar los últimos cambios del repositorio principal
git fetch upstream
git merge upstream/main

# 3. Actualizar la rama main de tu Fork personal
git push origin main

# 4. (Opcional) Traer las novedades a tu rama de trabajo
git checkout feature/nombre-de-tu-tarea
git rebase main
```

---

## 🛠️ Buenas Prácticas y Reglas del Proyecto

1. **Atención con el `.env`**: Nunca fuerces la inclusión de archivos `.env` o credenciales. Revisa siempre el `.gitignore`.
2. **Puertos e Infraestructura**: Si editas el `docker-compose.yml`, recuerda mantener el aislamiento de red de las tiendas y no mapear puertos duplicados hacia el host.
3. **Commits Limpios**: Realiza commits pequeños y frecuentes sobre la funcionalidad en la que estás trabajando.
