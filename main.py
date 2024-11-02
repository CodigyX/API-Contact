from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración SMTP
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

# Modelo de formulario
class ContactForm(BaseModel):
    name: str = Field(..., title="Name", min_length=2, max_length=50)
    last_name: str = Field(..., title="Last Name", min_length=2, max_length=50)
    email: EmailStr
    message: str = Field(..., title="Message", min_length=10, max_length=500)

# Función para enviar el correo de verificación
def send_verification_email(form_data: ContactForm, email_to: str, subject: str):
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        # Crear el mensaje de correo
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = email_to
        msg['Subject'] = subject

        # Adjuntar la imagen del banner
        with open("assets/escolaryx-banner.png", "rb") as img_file:
            img = MIMEImage(img_file.read())
            img.add_header('Content-ID', '<banner_image>')
            msg.attach(img)

        # HTML del cuerpo del correo
        html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <header style="text-align: center; padding: 10px;">
            <img src="cid:banner_image" alt="EscolaryX Banner" style="max-width: 100%; height: auto;">
        </header>
        <h2>Hola {form_data.name} {form_data.last_name},</h2>
        <p>Gracias por contactarnos. Hemos recibido tu mensaje:</p>
        <blockquote style="font-style: italic; padding-left: 20px; border-left: 3px solid #008080;">
            {form_data.message}
        </blockquote>
        <p>Nos pondremos en contacto contigo lo antes posible.</p>
        
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" integrity="sha384-k6RqeWeci5ZR/Lv4MR0sA0FfDOMq+ciR1KvW6zPjR3u4h5X+9vENW5G4F57CTJk" crossorigin="anonymous">

        <!-- Footer con Redes Sociales -->
        <footer style="text-align: center; margin-top: 20px;">
            <div style="font-size: 14px;">
                <p>¡Mundos fantásticos al alcance de tu mente!</p>
                <p>info@escolaryx.com | Teléfono: +52 272 100 8919</p>
                <div style="margin: 10px 0; font-size: 24px;">
                    <a href="https://facebook.com" style="text-decoration: none; color: #4267B2; margin-right: 10px;">
                        <i class="fab fa-facebook" style="color: #4267B2;"></i>
                    </a>
                    <a href="https://twitter.com" style="text-decoration: none; color: #1DA1F2; margin-right: 10px;">
                        <i class="fab fa-twitter" style="color: #1DA1F2;"></i>
                    </a>
                    <a href="https://instagram.com" style="text-decoration: none; color: #C13584; margin-right: 10px;">
                        <i class="fab fa-instagram" style="color: #C13584;"></i>
                    </a>
                    <a href="https://linkedin.com" style="text-decoration: none; color: #0077B5; margin-right: 10px;">
                        <i class="fab fa-linkedin" style="color: #0077B5;"></i>
                    </a>
                </div>
            </div>
            <p style="font-size: 12px; color: #777;">&copy; 2024 CodigyX. Todos los derechos reservados.</p>
        </footer>
    </body>
    </html>
"""

        msg.attach(MIMEText(html_body, 'html'))

        # Enviar el correo
        server.sendmail(SENDER_EMAIL, email_to, msg.as_string())
        server.quit()
    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send verification email")

# Endpoint del formulario de contacto
@app.post("/contact")
async def contact_form(form_data: ContactForm, background_tasks: BackgroundTasks):
    try:
        subject = "Verificación de correo electrónico"
        background_tasks.add_task(send_verification_email, form_data, form_data.email, subject)
        return {"message": "Formulario recibido. Se ha enviado un correo de verificación."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error al procesar el formulario")

# Ejecuta uvicorn si es el archivo principal
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
