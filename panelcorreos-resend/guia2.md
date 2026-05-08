# Guía de Instalación para Colaboradores (App de Escritorio)

Esta guía explica cómo generar la aplicación de escritorio (`.exe`) después de clonar el repositorio.

## Requisitos Previos

1.  **Python instalado:** Asegúrate de tener Python instalado en tu sistema Windows.
2.  **Archivo .env:** Asegúrate de tener un archivo `.env` en la raíz de la carpeta con las siguientes variables:
    ```env
    RESEND_API_KEY=tu_api_key_aqui
    SENDER_EMAIL=tu_correo_remitente@ejemplo.com
    ```

## Cómo Generar la Aplicación (.exe)

Para crear la aplicación de escritorio y poder usarla con solo un clic, sigue estos pasos:

1.  Abre la carpeta del proyecto en tu explorador de archivos.
2.  Busca el archivo llamado **`build_app.bat`**.
3.  Haz **doble clic** en el archivo `build_app.bat`.
4.  Se abrirá una ventana negra (terminal) que hará lo siguiente:
    -   Instalará las librerías necesarias automáticamente.
    -   Compilará el código en un solo archivo ejecutable.
    -   Limpiará los archivos temporales de construcción.
5.  Cuando termine, presiona cualquier tecla para cerrar la ventana.

## Dónde está la Aplicación

Una vez finalizado el proceso anterior, aparecerá una carpeta llamada **`dist`**.
Dentro de esa carpeta encontrarás el archivo:

👉 **`PanelCorreos.exe`**

¡Listo! Ya puedes copiar ese archivo a tu escritorio o donde prefieras y ejecutarlo con un doble clic cada vez que quieras enviar correos.

---
**Nota:** Si realizas cambios en el código (`main.py`), simplemente vuelve a ejecutar `build_app.bat` para actualizar la aplicación.
