import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

EMAIL_USERNAME = "adapbot@gmail.com"
EMAIL_PASSWORD = "AdapBot143"
SMTP_SERVER = "smtp.gmail.com:587"

#Files is an array of (payload, name) 2-tuples.
def send_mail(attached_file_name, recipients, files=[]):
    """
    This is an helper function for sending the data to your email
    :param attached_file_name: file to send (full path)
    :param recipients: comma separated list of email recipients
    :return: None
    """
    email_message = MIMEMultipart()
    email_message['Subject'] = 'Experiment Data'
    email_message['From'] = EMAIL_USERNAME
    try:
        email_message['To'] = ", ".join(recipients)
    except Exception:
        email_message['To'] = recipients #one recipient
            
    email_message['Date'] = formatdate(localtime=True)
    email_message.attach(MIMEText("Your experiment has finished!"))

    attachFile(email_message,filename=attached_file_name,name=attached_file_name.split('/')[-1])
    for f,name in files:
        attachFile(email_message,payload=f,name=name)
    #attachFile(email_message,payload=attached_file_name)
    send_email_connection = smtplib.SMTP(SMTP_SERVER)
    send_email_connection.starttls()
    try:
        send_email_connection.login(EMAIL_USERNAME, EMAIL_PASSWORD)

        send_email_connection.sendmail(
            EMAIL_USERNAME,
            recipients,
            email_message.as_string()
        )

        send_email_connection.quit()
    except Exception:
        print("Failed to send email, credentials failed.")
        print("This can also happen when 'new location is detected'")

def attachFile(email,payload=None,name=None,filename=None):
    attach = MIMEBase('application', 'octet-stream')
    if payload is not None:
        attach.set_payload(payload)
        if ".png" not in name: name+=".png"
    elif filename is not None:
        attach.set_payload(open(filename, 'rb').read())
    else:
        print("No attachments")
        return
    encoders.encode_base64(attach)
    attach.add_header('Content-Disposition', 'attachment; filename="%s"'%name)
    email.attach(attach)
