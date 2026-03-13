# 📊 WhatsApp Insights Platform

Una plataforma analítica premium construida con Streamlit para visualizar y analizar conversaciones de WhatsApp. Este dashboard permite monitorear la participación de los usuarios, filtrar por fechas y detectar quién no está hablando en el grupo.

## 🚀 Características

- **Diseño Premium**: Interfaz moderna con fuentes Inter, efectos de desenfoque (glassmorphism) e indicadores visuales claros.
- **Clasificación Automática**: Los usuarios se dividen en grupos según su nivel de actividad:
  - 🟢 **Alta Actividad**: Usuarios muy participativos.
  - 🟠 **Actividad Moderada**: Usuarios con participación baja o media.
  - 🔴 **Inactividad Detectada**: Usuarios que no han enviado mensajes en el periodo seleccionado.
- **Buscador de Mensajes**: Selecciona un usuario para ver su historial completo de mensajes.
- **Filtro Temporal**: Selector de rango de fechas dinámico.
- **Gestión de Contactos Persistente**: Lista de usuarios editable que se guarda automáticamente en `users.json`.
- **Coincidencia Inteligente**: Sistema robusto que ignora emojis y variaciones de formato (como las virgulillas `~`) para asegurar que los nombres coincidan perfectamente con tu lista de contactos.

## 🛠️ Instalación

Asegúrate de tener [uv](https://github.com/astral-sh/uv) instalado.

1. Instala las dependencias:
   ```bash
   uv sync
   ```

2. Ejecuta la aplicación:
   ```bash
   uv run streamlit run main.py
   ```

## 📋 Cómo usar el Dashboard

1. **Exportar Chat**: Abre el chat de WhatsApp en tu móvil -> Configuración -> Exportar chat -> Sin archivos.
2. **Subir Archivo**: Arrastra el archivo `.txt` generado a la barra lateral de la aplicación.
3. **Analizar**: Usa la pestaña de "Resumen de Actividad" para ver los grupos de usuarios.
4. **Filtrar**: Ajusta las fechas en la barra lateral para ver la actividad en momentos específicos.
5. **Gestionar**: Añade o elimina nombres en la lista de "Gestión de Lista" para que el detector de inactividad sepa a quién vigilar.

## 📁 Estructura del Proyecto

- `main.py`: Lógica principal del dashboard de Streamlit.
- `user_manager.py`: Módulo para la gestión y persistencia de la lista de contactos.
- `users.json`: Archivo donde se guardan tus contactos a vigilar.
- `.gitignore`: Configuración para evitar subir archivos temporales o personales.

---
*Desarrollado para análisis de datos de mensajería instantánea.*
