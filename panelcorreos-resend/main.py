import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import resend
import os
import threading
import base64
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configurar variables de entorno
resend.api_key = os.getenv("RESEND_API_KEY")
default_sender = os.getenv("SENDER_EMAIL")

class EmailSenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Resend Email Sender")
        self.root.geometry("650x700")
        
        # Estilos generales
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        
        # Colores y fuentes
        bg_color = "#f4f4f9"
        self.root.configure(bg=bg_color)
        
        style.configure('TFrame', background=bg_color)
        style.configure('TLabelframe', background=bg_color, font=('Segoe UI', 11, 'bold'))
        style.configure('TLabelframe.Label', background=bg_color, font=('Segoe UI', 11, 'bold'), foreground="#333333")
        style.configure('TLabel', background=bg_color, font=('Segoe UI', 10), foreground="#555555")
        style.configure('Header.TLabel', background=bg_color, font=('Segoe UI', 16, 'bold'), foreground="#2c3e50")
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=6)
        
        # Scrollable area config
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.main_container, bg=bg_color, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=self.canvas.winfo_width())
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=e.width))

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Frame interno con padding
        self.content_frame = ttk.Frame(self.scrollable_frame, padding=20)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        self.recipients = []
        self.attachments = []

        self.create_widgets()

        # Configurar scroll con rueda del ratón
        self.root.bind("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def create_widgets(self):
        parent = self.content_frame
        
        # Título y subtítulo
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(header_frame, text="🚀 Panel de Envío de Correos", style='Header.TLabel').pack(anchor=tk.CENTER)
        ttk.Label(header_frame, text="Envía correos personalizados fácilmente a través de Resend.", font=('Segoe UI', 10, 'italic')).pack(anchor=tk.CENTER, pady=(5,0))

        # --- Remitente ---
        frame_sender = ttk.LabelFrame(parent, text=" 👤 Remitente ", padding=15)
        frame_sender.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(frame_sender, text="De:").pack(side=tk.LEFT)
        self.sender_var = tk.StringVar(value=default_sender)
        ttk.Entry(frame_sender, textvariable=self.sender_var, width=50, font=('Segoe UI', 10)).pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # --- Destinatarios ---
        frame_recipients = ttk.LabelFrame(parent, text=" 👥 Destinatarios ", padding=15)
        frame_recipients.pack(fill=tk.X, pady=(0, 15))
        
        top_rec = ttk.Frame(frame_recipients)
        top_rec.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(top_rec, text="Añadir Correo:").pack(side=tk.LEFT)
        self.new_email_var = tk.StringVar()
        self.new_email_entry = ttk.Entry(top_rec, textvariable=self.new_email_var, width=30, font=('Segoe UI', 10))
        self.new_email_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.new_email_entry.bind('<Return>', lambda e: self.add_recipient())
        
        ttk.Button(top_rec, text="➕ Añadir", command=self.add_recipient).pack(side=tk.LEFT)
        
        # Lista de destinatarios
        self.recipients_listbox = tk.Listbox(frame_recipients, height=4, font=('Segoe UI', 10), relief="flat", highlightbackground="#cccccc", highlightthickness=1)
        self.recipients_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        btn_rec = ttk.Frame(frame_recipients)
        btn_rec.pack(fill=tk.X)
        ttk.Button(btn_rec, text="🗑️ Eliminar Seleccionado", command=self.remove_recipient).pack(side=tk.LEFT)
        ttk.Button(btn_rec, text="🧹 Limpiar Lista", command=self.clear_recipients).pack(side=tk.LEFT, padx=10)

        # --- Mensaje ---
        frame_msg = ttk.LabelFrame(parent, text=" ✉️ Contenido del Mensaje ", padding=15)
        frame_msg.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        ttk.Label(frame_msg, text="Asunto:").pack(anchor=tk.W, pady=(0, 5))
        self.subject_var = tk.StringVar()
        ttk.Entry(frame_msg, textvariable=self.subject_var, font=('Segoe UI', 10)).pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(frame_msg, text="Mensaje (Soporta HTML básico):").pack(anchor=tk.W, pady=(0, 5))
        self.message_text = scrolledtext.ScrolledText(frame_msg, height=10, font=('Segoe UI', 10), relief="flat", highlightbackground="#cccccc", highlightthickness=1)
        self.message_text.pack(fill=tk.BOTH, expand=True)

        # --- Adjuntos ---
        frame_attachments = ttk.LabelFrame(parent, text=" 📎 Archivos Adjuntos ", padding=15)
        frame_attachments.pack(fill=tk.X, pady=(0, 15))
        
        btn_att_top = ttk.Frame(frame_attachments)
        btn_att_top.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(btn_att_top, text="📎 Añadir Archivo", command=self.add_attachment).pack(side=tk.LEFT)
        ttk.Label(btn_att_top, text="(PDF, Word, JPG, PNG)", foreground="#888888", font=('Segoe UI', 9)).pack(side=tk.LEFT, padx=10)
        
        self.attachments_listbox = tk.Listbox(frame_attachments, height=3, font=('Segoe UI', 10), relief="flat", highlightbackground="#cccccc", highlightthickness=1)
        self.attachments_listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Button(frame_attachments, text="🗑️ Quitar Seleccionado", command=self.remove_attachment).pack(side=tk.LEFT)

        # --- Acciones ---
        frame_actions = ttk.Frame(parent)
        frame_actions.pack(fill=tk.X, pady=(10, 20))
        
        self.send_btn = ttk.Button(frame_actions, text="📤 Enviar Mensaje", command=self.start_sending)
        self.send_btn.pack(side=tk.RIGHT)
        
        self.status_var = tk.StringVar(value="Esperando acción...")
        ttk.Label(frame_actions, textvariable=self.status_var, foreground="#666666", font=('Segoe UI', 10, 'italic')).pack(side=tk.LEFT)

    def add_recipient(self):
        email = self.new_email_var.get().strip()
        if email and email not in self.recipients:
            self.recipients.append(email)
            self.recipients_listbox.insert(tk.END, email)
            self.new_email_var.set("")
        elif email in self.recipients:
            messagebox.showwarning("Atención", "El correo ya está en la lista.")
            
    def remove_recipient(self):
        selected_idx = self.recipients_listbox.curselection()
        if selected_idx:
            idx = selected_idx[0]
            email = self.recipients_listbox.get(idx)
            self.recipients.remove(email)
            self.recipients_listbox.delete(idx)

    def clear_recipients(self):
        self.recipients.clear()
        self.recipients_listbox.delete(0, tk.END)

    def add_attachment(self):
        filetypes = (
            ('Todos los soportados', '*.pdf *.docx *.doc *.jpg *.jpeg *.png'),
            ('Documentos PDF', '*.pdf'),
            ('Documentos Word', '*.docx *.doc'),
            ('Imágenes', '*.jpg *.jpeg *.png'),
            ('Todos los archivos', '*.*')
        )
        
        filename = filedialog.askopenfilename(
            title='Seleccionar archivo para adjuntar',
            initialdir='/',
            filetypes=filetypes
        )
        
        if filename:
            if filename not in self.attachments:
                self.attachments.append(filename)
                self.attachments_listbox.insert(tk.END, os.path.basename(filename))
            else:
                messagebox.showwarning("Atención", "El archivo ya ha sido seleccionado.")

    def remove_attachment(self):
        selected_idx = self.attachments_listbox.curselection()
        if selected_idx:
            idx = selected_idx[0]
            self.attachments.pop(idx)
            self.attachments_listbox.delete(idx)

    def clear_attachments(self):
        self.attachments.clear()
        self.attachments_listbox.delete(0, tk.END)

    def start_sending(self):
        if not self.recipients:
            messagebox.showwarning("Faltan Destinatarios", "Añade al menos un correo a la lista.")
            return
            
        subject = self.subject_var.get().strip()
        if not subject:
            messagebox.showwarning("Falta Asunto", "Por favor, escribe un asunto para el correo.")
            return
            
        message = self.message_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Falta Mensaje", "Por favor, escribe el contenido del mensaje.")
            return

        self.send_btn.config(state=tk.DISABLED)
        self.status_var.set("⏳ Enviando correos...")
        self.root.update_idletasks()
        
        # Usar un hilo para no congelar la interfaz gráfica mientras se envían
        threading.Thread(target=self.send_emails, args=(subject, message), daemon=True).start()

    def send_emails(self, subject, message):
        sender = self.sender_var.get().strip()
        
        try:
            # Reemplazar saltos de línea por etiquetas <br> para mantener el formato en HTML
            html_content = message.replace('\n', '<br>')
            
            # Preparar adjuntos
            attachments_data = []
            for file_path in self.attachments:
                try:
                    with open(file_path, "rb") as f:
                        content = base64.b64encode(f.read()).decode('utf-8')
                        attachments_data.append({
                            "content": content,
                            "filename": os.path.basename(file_path)
                        })
                except Exception as e:
                    print(f"Error al procesar adjunto {file_path}: {e}")

            params = {
                "from": sender,
                "to": self.recipients,
                "subject": subject,
                "html": f"<div style='font-family: sans-serif, Arial;'>{html_content}</div>",
                "text": message
            }
            
            if attachments_data:
                params["attachments"] = attachments_data
            
            response = resend.Emails.send(params)
            
            self.root.after(0, self.on_send_complete, True, response)
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, self.on_send_complete, False, error_msg)

    def on_send_complete(self, success, details):
        self.send_btn.config(state=tk.NORMAL)
        if success:
            msg_id = details.get('id', 'Desconocido') if isinstance(details, dict) else details
            self.status_var.set(f"✅ Enviado exitosamente (ID: {msg_id})")
            messagebox.showinfo("Éxito", f"El correo fue enviado a Resend correctamente.\n\nID de Mensaje: {msg_id}\n\n IMPORTANTE: El correo no aparecera en la bandeja de entrada, solo aparecera en SPAM o Correo no deseado. Mensajes con asunto 'hola' o palabras pequeñas suelen ser filtrados automáticamente por Gmail.")
            self.message_text.delete("1.0", tk.END)
            self.subject_var.set("")
            self.clear_recipients()
            self.clear_attachments()
        else:
            self.status_var.set("❌ Error al enviar.")
            messagebox.showerror("Error", f"Ocurrió un error al enviar:\n{details}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EmailSenderApp(root)
    root.mainloop()
