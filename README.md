# ChaniWeb - Sistema de Comparación de Precios de Supermercados

## Descripción General

ChaniWeb es una plataforma web desarrollada para unificar y comparar los precios de productos de primera necesidad entre diferentes cadenas de supermercados en Ecuador (Mi comisariato, Aki, entre otros). El proyecto nace de la necesidad de los consumidores de optimizar su presupuesto familiar sin tener que visitar físicamente múltiples establecimientos o revisar diversos sitios web.

El sistema opera bajo una arquitectura de microservicios distribuida, diseñada para ser escalable y resiliente, siguiendo las mejores prácticas de desarrollo "Cloud-Native".

## Arquitectura del Sistema

El proyecto implementa una arquitectura desacoplada donde cada componente tiene una responsabilidad única. Actualmente, esta arquitectura se simula localmente utilizando Docker Compose para replicar un entorno de producción en la nube.

Componentes principales:

1.  **Frontend (Nginx + React):**

    - Actúa como el punto de entrada para el usuario.
    - Utiliza Nginx como servidor web y Proxy Inverso.
    - Gestiona el enrutamiento de peticiones hacia el Backend, eliminando problemas de CORS y ocultando la topología interna de la red.

2.  **Backend (FastAPI - Python):**

    - API RESTful que gestiona la lógica de negocio.
    - Procesa las consultas de productos y normaliza los datos recibidos.

3.  **Base de Datos (PostgreSQL):**

    - Motor de base de datos relacional para la persistencia de la información de productos y precios.

4.  **Scrapers (Workers Python):**
    - Procesos en segundo plano encargados de la ingesta de datos.
    - Implementan lógica de "espera activa" para asegurar que el sistema esté disponible antes de enviar información.

## Evolución del Proyecto (Metodología Scrum)

El desarrollo del proyecto se ha realizado mediante incrementos funcionales (Sprints). A continuación se detalla el alcance y los logros técnicos de cada etapa.

### Sprint 1: Desarrollo del Núcleo y Entorno Local

**Objetivo:** Establecer la comunicación básica entre los servicios en un entorno de desarrollo.

- **Alcance:** Se crearon los contenedores básicos para el Frontend, Backend y Base de Datos.
- **Limitaciones:** La comunicación se realizaba mediante puertos expuestos directamente (`localhost:8000`). El Frontend contenía direcciones IP fijas en su código fuente, lo cual es funcional para desarrollo en una sola máquina, pero inseguro e inviable para un despliegue real.
- **Resultado:** MVP funcional con carga de datos manual.

### Sprint 2: Simulación de Entorno de Producción (Estado Actual)

**Objetivo:** Refactorizar la arquitectura para soportar un despliegue profesional y robusto, simulando condiciones de nube (Azure/Kubernetes).

- **Implementación de Proxy Inverso:** Se configuró Nginx dentro del contenedor de Frontend. Ahora, la aplicación no expone el puerto del API al cliente. Las peticiones se realizan a rutas relativas (`/api/products`), y Nginx las redirige internamente dentro de la red privada de Docker.
- **Tolerancia a Fallos:** Se solucionó el problema de "Race Conditions" (condiciones de carrera) donde los servicios fallaban al iniciar porque la base de datos aún no estaba lista.
- **Limpieza de Código:** Se eliminaron todas las referencias a `localhost` dentro del código fuente de React, permitiendo que la aplicación sea agnóstica al entorno donde se despliega.

## Justificación de la Simulación Local

Para validar la arquitectura de producción sin incurrir en los costos y la complejidad operativa de mantener un clúster de Kubernetes activo durante la fase de desarrollo, se utiliza **Docker Compose** configurado para imitar la red de producción.

Esto permite al equipo:

1.  Validar la comunicación entre servicios mediante nombres de host internos (DNS de Docker).
2.  Probar la configuración del servidor web Nginx.
3.  Asegurar la persistencia de datos y la recuperación ante fallos de los contenedores.

## Requisitos Previos

Para ejecutar este proyecto en su máquina local, asegúrese de tener instalado:

- **Docker Desktop** (versión actualizada).
- **Git** (para el control de versiones).

## Guía de Instalación y Ejecución

Siga estos pasos para desplegar el entorno completo de simulación.

### 1. Construcción y Despliegue

Abra una terminal en la carpeta raíz del proyecto y ejecute el siguiente comando. Este comando compilará el código fuente del Frontend, construirá las imágenes de Docker y levantará los servicios en el orden correcto.

````bash
docker-compose up --build
### 2. Acceso a la Aplicación
Una vez que la terminal muestre que los servicios se han iniciado correctamente, abra su navegador web preferido e ingrese a la siguiente dirección:

**http://localhost**

> **Nota:** No es necesario especificar puertos (como `:3000`). La aplicación se sirve a través del puerto estándar HTTP (80) gracias a la configuración del servidor web.

### 3. Verificación de Funcionamiento
*   Deberá visualizar la tabla de productos con información proveniente de los supermercados simulados (Mi comisariato y Aki).
*   No debe visualizar mensajes de carga infinita ni errores de conexión.

### 4. Detener el Entorno
Para detener la ejecución y apagar los contenedores de manera ordenada, presione `Ctrl + C` en la terminal donde se ejecuta el proceso. Alternativamente, puede abrir una nueva terminal en la carpeta del proyecto y ejecutar:

```bash
docker-compose down

## Estructura de Carpetas

*   **`/backend`**: Contiene el código fuente del API desarrollado en FastAPI, encargado de la lógica de negocio y procesamiento de datos.
*   **`/frontend`**: Contiene el código fuente en React, el archivo de configuración de Nginx (`nginx.conf`) y el Dockerfile optimizado para producción.
*   **`/scrapers`**: Scripts en Python encargados de la simulación de extracción de datos y el envío de información al backend.
*   **`/k8s-azure`**: Archivos de manifiesto YAML (Deployments, Services, ConfigMaps) destinados para el futuro despliegue en Azure Kubernetes Service (AKS).
*   **`docker-compose.yml`**: Archivo de orquestación que define los servicios, redes y volúmenes para ejecutar la simulación local.
````
