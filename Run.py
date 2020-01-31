import os
import sys
import smtplib
import logging
import email.utils

from MyLists import app
from email.message import EmailMessage
from logging.handlers import RotatingFileHandler, SMTPHandler


formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
handler = RotatingFileHandler("MyLists/static/log/mylists.log", maxBytes=10000000, backupCount=5)
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)


if not app.debug:
    class SSLSMTPHandler(SMTPHandler):
        def emit(self, record):
            """ Emit a record. """
            try:
                port = self.mailport
                if not port:
                    port = smtplib.SMTP_PORT
                smtp = smtplib.SMTP_SSL(self.mailhost, port)
                msg = EmailMessage()
                msg['From'] = self.fromaddr
                msg['To'] = ','.join(self.toaddrs)
                msg['Subject'] = self.getSubject(record)
                msg['Date'] = email.utils.localtime()
                msg.set_content(self.format(record))
                if self.username:
                    smtp.login(self.username, self.password)
                smtp.send_message(msg, self.fromaddr, self.toaddrs)
                smtp.quit()
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                self.handleError(record)
    mail_handler = SSLSMTPHandler(mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                                  fromaddr=app.config['MAIL_USERNAME'],
                                  toaddrs=app.config['MAIL_ADMIN'],
                                  subject='Mylists - exceptions occurred!',
                                  credentials=(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']))
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)


if not os.path.isfile('./config.ini'):
    print("Config file not found. Exit.")
    sys.exit()


if __name__ == "__main__":
    app.run(debug=True)
