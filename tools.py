import logging
from livekit.agents import function_tool, RunContext
import requests
from langchain_community.tools import DuckDuckGoSearchRun
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
import subprocess
import logging
from livekit.agents import function_tool, RunContext
from dotenv import load_dotenv

load_dotenv()


@function_tool()
async def get_weather(context: RunContext, city: str) -> str:
    """get the current weather for a given city"""
    try:
        response = requests.get(f"https://wttr.in/{city}?format=3")

        if response.status_code == 200:
            logging.info(f"Weather for {city}: {response.text.strip()}")
            return response.text.strip()
        else:
            logging.error(f"Failed to get weather for {city}: {response.status_code}")
            return f"Could not retrieve weather for {city}."
    except Exception as e:
        logging.error(f"Failed to get weather for {city}: {e}")
        return f"Could not retrieve weather for {city}."


@function_tool()
async def search_web(context: RunContext, query: str) -> str:
    """Search the web for a given query and give the direct results not repeat the query and do not say tool_output, direct give the answer but somtime you can repeat a part of the question"""
    try:
        result = DuckDuckGoSearchRun().run(tool_input=query)
        logging.info(f"Search result for {query}: {result}")
        return result
    except Exception as e:
        logging.error(f"Failed to search web for {query}: {e}")
        return f"Could not search web for {query}."


@function_tool()
async def send_email(
    to_email: str, subject: str, message: str, cc_email: Optional[str] = None
) -> str:
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")

        if not gmail_user or not gmail_password:
            return "Email sending failed: Gmail credentials not configured."

        msg = MIMEMultipart()
        msg["From"] = gmail_user
        msg["To"] = to_email
        msg["Subject"] = subject

        recipients = [to_email]
        if cc_email:
            msg["Cc"] = cc_email
            recipients.append(cc_email)

        msg.attach(MIMEText(message, "plain"))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, recipients, msg.as_string())
        server.quit()
        logging.info(f"Email sent successfully to {to_email}")
        return f"Email sent successfully to {to_email}"

    except smtplib.SMTPAuthenticationError:
        logging.error("Authentication error. Check Gmail credentials. ")
        return "Authentication error. Check Gmail credentials."
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
        return f"Email sending failed: SMTP error - {str(e)}"
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")
        return f"Error sending email: {str(e)}"


@function_tool()
async def open_app(context: RunContext, app_name: str) -> str:
    """
    Open an installed application on the system by name.
    Example: 'notepad', 'chrome', 'youtube', 'calculator'
    """
    # Map known app names to their launch commands
    app_commands = {
        # Core Windows Apps
        "settings": "start ms-settings:",
        "camera": "start microsoft.windows.camera:",
        "notepad": "notepad",
        "calculator": "calc",
        "explorer": "explorer",
        "cmd": "cmd",
        "command prompt": "cmd",
        "powershell": "powershell",
        "task manager": "taskmgr",
        "settings": "start ms-settings:",
        "control panel": "control",
        # Browsers
        "chrome": "start chrome",
        "youtube": "start chrome https://www.youtube.com",
        "github": "start https://github.com",
        "linkedin": "start https://www.linkedin.com",
        "email": "start https://mail.google.com",  # Gmail ke liye
        "gmail": "start https://mail.google.com",
        # Microsoft Office
        "word": "start winword",
        "microsoft word": "start winword",
        "excel": "start excel",
        "powerpoint": "start powerpnt",
        "onenote": "start onenote",
        "outlook": "start outlook",
        "access": "start msaccess",
        # Dev Tools (custom paths as per your system)
        "vs code": r'"C:\Users\amit_\AppData\Local\Programs\Microsoft VS Code\Code.exe"',
        "visual studio code": r'"C:\Users\amit_\AppData\Local\Programs\Microsoft VS Code\Code.exe"',
        "postman": r'"C:\Users\amit_\AppData\Local\Postman\Postman.exe"',
        "android studio": r'"C:\Program Files\Android\Android Studio\bin\studio64.exe"',
        "tableau": r'"C:\Program Files\Tableau\Tableau Public 2025.2\bin\tabpublic.exe"',
        # Media
        "vlc": "start vlc",
        "windows media player": "start wmplayer",
        "spotify": "start spotify",
        # Cloud
        "onedrive": "start onedrive",
        "google drive": "start googledrive",
        # Messaging
        # WhatsApp installed via Microsoft Store doesn't work with traditional path.
        # So this below command uses protocol if registered
        "whatsapp": "start shell:AppsFolder\\5319275A.WhatsAppDesktop_cv1g1gvanyjgm!App",
    }

    try:
        app_name_lower = app_name.lower()

        if app_name_lower in app_commands:
            subprocess.Popen(app_commands[app_name_lower], shell=True)
            logging.info(f"Opening {app_name}")
            return f"Opening {app_name}..."
        else:
            logging.warning(f"App '{app_name}' not recognized.")
            return f"Sorry, I couldn't find an app named '{app_name}'."

    except Exception as e:
        logging.error(f"Error opening app '{app_name}': {e}")
        return f"Failed to open '{app_name}': {str(e)}"
