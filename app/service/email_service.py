import mailtrap as mt

from app.config_settings.settings import settings

mailtrap_client = mt.MailtrapClient(token=settings.MAILTRAP_TOKEN, sandbox=True, inbox_id='3255993')

def send_todo_export_email(recipient: str):
    mail = mt.Mail(sender=mt.Address(email="welcome@todo.com"), to=[mt.Address(email=recipient)], subject="Welcome to todo world",text="You can use our app now")

    mailtrap_client.send(mail)