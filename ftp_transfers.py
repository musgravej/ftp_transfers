import configparser
import ftplib
import os
import pysftp
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Globals:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read(os.path.join(os.curdir, 'config.ini'))

        self.destination_path = config['PATHS']['destination_path']

        self.host = config['FTP']['host']
        self.user = config['FTP']['user']
        self.password = config['FTP']['password']
        self.path = config['FTP']['path']
        self.protocol = config['FTP']['protocol']
        self.transfer_files = ('V2FBLUSERDATA.TXT', 'OFFHRS.TXT', 'OFFFED.TXT')
        self.success = set()

        self.email_to = config['EMAIL']['email_to']
        self.email_from = config['EMAIL']['email_from']
        self.email_user = config['EMAIL']['email_user']
        self.email_password = config['EMAIL']['email_password']
        self.email_server = config['EMAIL']['email_server']

    def set_encrypt_date(self):
        pass


def transfer_to_ftp():

    if g.protocol == 'sftp':
        with pysftp.Connection(host=g.host, username=g.user, password=g.password) as sftp_conn:
            with sftp_conn.cd(g.path):
                for f in sftp_conn.listdir():
                    if f in g.transfer_files:
                        print(f"Downloading {f}")
                        g.success.add(f)
                        sftp_conn.get(f, os.path.join(g.destination_path, f))


def send_email_message():
    port = 587
    smtp_server = g.email_server
    sender_email = g.email_user
    email_from = g.email_from
    receiver_email = g.email_to
    password = g.email_password
    download_time = datetime.datetime.strftime(datetime.datetime.now(),
                                               "%Y-%m-%d %H:%M")

    fle_format = "file has" if len(g.success) == 1 else "files have"
    table_data = ""
    for filename in g.success:
        table_data += f"<tr><td>{filename}</td></tr>"

    text = "Transfer complete"

    html = ("<html> <head> <style> td, th {{ border: 1px solid #dddddd; text-align: left; padding: 8px;}}"
            "</style> </head> <body> <p>The following {fle_format} been been downloaded from the FTP:<br> "
            "</p> <table width: 100%;> <tr> <th>File</th> </tr> "
            "{table_data} </table> </body> </html> "
            "<p>Files have been saved to {destination} </p>".format(table_data=table_data,
                                                                    fle_format=fle_format,
                                                                    destination=str.replace(g.destination_path,
                                                                                            "\\\\", "\\")))

    message = MIMEMultipart("alternative")
    message["Subject"] = f"FTP download complete: {download_time}"
    message["From"] = sender_email
    message["To"] = receiver_email

    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))

    with smtplib.SMTP(smtp_server, port) as server:
        # server.set_debuglevel(1)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(email_from, receiver_email, message.as_string())


def main():
    pass


if __name__ == '__main__':
    global g
    global gpg
    g = Globals()
    transfer_to_ftp()
    if len(g.success) > 0:
        send_email_message()
