import aiosmtplib 
import asyncio
from email.message import EmailMessage
from faststream.rabbit import RabbitBroker, RabbitQueue
from faststream import FastStream
from pydantic import BaseModel, EmailStr

from sendler_config import sendler_settings, rabbit_settings
from log_conf import logger

#send email-message to user email 


log = logger()

pss = sendler_settings.sendler_pass

Email = sendler_settings.sendler_email

broker = RabbitBroker(url=rabbit_settings.rabbitmq_url)
app = FastStream(broker)

queue = RabbitQueue('main', durable=True)

class SendlerResponse(BaseModel):
    status: str
    email: EmailStr

@broker.subscriber(queue)
async def accept_message(mseg: SendlerResponse):
    """listening to checker and send message to users"""

    
    if mseg.status == 'fell':
        log.info('send')
        letter = EmailMessage()
        letter.set_content('price was fell')
        letter['Subject'] = 'the price was fell'
        letter['From'] = Email
        letter['To'] = mseg.email
        async with aiosmtplib.SMTP(hostname='smtp.gmail.com', port=587, start_tls=True) as smtp_server:
            await smtp_server.login(Email, pss)
            await smtp_server.send_message(letter)

if __name__ == "__main__":
    import asyncio
    asyncio.run(app.run())





