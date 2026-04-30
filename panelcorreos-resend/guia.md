# Panel de Correos - Resend

Esta es una mini aplicación de escritorio en Python para enviar correos electrónicos fácilmente utilizando la API de Resend. Cuenta con una interfaz gráfica amigable que permite configurar el asunto, mensaje y gestionar una lista de destinatarios.

## Requisitos Previos

Asegúrate de tener instalado Python en tu sistema local.

## Instalación

1. Abre tu terminal (Símbolo del sistema, PowerShell, etc.).
2. Ubícate en esta carpeta `panelcorreos-resend`.
3. Instala la dependencia necesaria ejecutando:

```bash
pip install -r requirements.txt
```

## Uso

Para iniciar la aplicación en tu entorno local, simplemente ejecuta el archivo principal:

```bash
python main.py
```

### Funciones de la Interfaz

- **Remitente:** Puedes modificar el remitente (De:) que por defecto es el de tu dominio configurado (`dafne@famatconsulting.com`).
- **Destinatarios:** Escribe un correo y presiona "Añadir" (o la tecla Enter). Puedes agregar todos los correos a los que desees enviar el mensaje a la vez. También puedes eliminar correos de la lista seleccionándolos o limpiar la lista por completo.
- **Asunto:** El título de tu correo electrónico.
- **Mensaje:** El cuerpo de tu correo. Soporta saltos de línea e incluso etiquetas HTML básicas (como `<b>` para negrita o `<a href="...">` para enlaces).
- **Enviar Mensaje:** Al hacer clic, el panel procesará la lista de destinatarios y enviará el correo utilizando tu API Key de Resend (ya preconfigurada).
