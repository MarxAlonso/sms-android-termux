import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import resend
import os
import threading
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configurar API Key proporcionada en el .env
resend.api_key = os.getenv("RESEND_API_KEY")

class EmailSenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Resend Email Sender")
        self.root.geometry("600x650")
        self.root.configure(padx=20, pady=20)
        
        # Estilos
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=5)
        style.configure('TLabel', font=('Segoe UI', 10))
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'))
        
        self.recipients = []

        self.create_widgets()

    def create_widgets(self):
        # Título
        ttk.Label(self.root, text="🚀 Panel de Envío de Correos", style='Header.TLabel').pack(pady=(0, 15))

        # --- Remitente ---
        frame_sender = ttk.LabelFrame(self.root, text="Remitente", padding=10)
        frame_sender.pack(fill=tk.X, pady=5)
        
        ttk.Label(frame_sender, text="De:").pack(side=tk.LEFT)
        self.sender_var = tk.StringVar(value="Dafne <dafne@famatconsulting.com>")
        ttk.Entry(frame_sender, textvariable=self.sender_var, width=50).pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        # --- Destinatarios ---
        frame_recipients = ttk.LabelFrame(self.root, text="Destinatarios", padding=10)
        frame_recipients.pack(fill=tk.BOTH, expand=True, pady=5)
        
        top_rec = ttk.Frame(frame_recipients)
        top_rec.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(top_rec, text="Añadir Correo:").pack(side=tk.LEFT)
        self.new_email_var = tk.StringVar()
        self.new_email_entry = ttk.Entry(top_rec, textvariable=self.new_email_var, width=30)
        self.new_email_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.new_email_entry.bind('<Return>', lambda e: self.add_recipient())
        
        ttk.Button(top_rec, text="Añadir", command=self.add_recipient).pack(side=tk.LEFT)
        
        # Lista de destinatarios
        self.recipients_listbox = tk.Listbox(frame_recipients, height=5, font=('Segoe UI', 10))
        self.recipients_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        btn_rec = ttk.Frame(frame_recipients)
        btn_rec.pack(fill=tk.X)
        ttk.Button(btn_rec, text="Eliminar Seleccionado", command=self.remove_recipient).pack(side=tk.LEFT)
        ttk.Button(btn_rec, text="Limpiar Lista", command=self.clear_recipients).pack(side=tk.LEFT, padx=10)

        # --- Mensaje ---
        frame_msg = ttk.LabelFrame(self.root, text="Contenido del Mensaje", padding=10)
        frame_msg.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(frame_msg, text="Asunto:").pack(anchor=tk.W)
        self.subject_var = tk.StringVar()
        ttk.Entry(frame_msg, textvariable=self.subject_var).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame_msg, text="Mensaje (Soporta HTML básico):").pack(anchor=tk.W)
        self.message_text = scrolledtext.ScrolledText(frame_msg, height=10, font=('Segoe UI', 10))
        self.message_text.pack(fill=tk.BOTH, expand=True)

        # --- Acciones ---
        frame_actions = ttk.Frame(self.root)
        frame_actions.pack(fill=tk.X, pady=15)
        
        self.send_btn = ttk.Button(frame_actions, text="📤 Enviar Mensaje", command=self.start_sending)
        self.send_btn.pack(side=tk.RIGHT)
        
        self.status_var = tk.StringVar(value="Listo.")
        ttk.Label(frame_actions, textvariable=self.status_var, foreground="gray").pack(side=tk.LEFT)

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
        self.status_var.set("Enviando correos...")
        self.root.update_idletasks()
        
        # Usar un hilo para no congelar la interfaz gráfica mientras se envían
        threading.Thread(target=self.send_emails, args=(subject, message), daemon=True).start()

    def send_emails(self, subject, message):
        sender = self.sender_var.get().strip()
        
        try:
            # Reemplazar saltos de línea por etiquetas <br> para mantener el formato en HTML
            html_content = message.replace('\n', '<br>')
            
            params = {
                "from": sender,
                "to": self.recipients,
                "subject": subject,
                "html": f"<div style='font-family: sans-serif, Arial;'>{html_content}</div>"
            }
            
            response = resend.Emails.send(params)
            
            self.root.after(0, self.on_send_complete, True, len(self.recipients))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, self.on_send_complete, False, error_msg)

    def on_send_complete(self, success, details):
        self.send_btn.config(state=tk.NORMAL)
        if success:
            self.status_var.set(f"✅ Enviado exitosamente a {details} destinatario(s).")
            messagebox.showinfo("Éxito", "Los correos han sido enviados correctamente.")
            self.message_text.delete("1.0", tk.END)
            self.subject_var.set("")
            self.clear_recipients()
        else:
            self.status_var.set("❌ Error al enviar.")
            messagebox.showerror("Error", f"Ocurrió un error al enviar:\n{details}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EmailSenderApp(root)
    root.mainloop()
