from pydantic_settings import BaseSettings, SettingsConfigDict


class SendlerSettings(BaseSettings):
    sendler_pass: str
    sendler_email: str


    model_config = SettingsConfigDict(
        env_file = 'sendler.env',
        env_file_encoding = 'utf-8',
        extra = 'ignore',
        case_sensitive = False,
    )
    


class RabbitMQSettings(BaseSettings):
    rabbit_pass: str = 'guest'
    rabbit_login: str = 'guest'
    rabbit_host: str = 'rabbit'
    rabbit_port: int = 5672


    model_config = SettingsConfigDict(
        env_file = 'sendler.env',
        env_file_encoding = 'utf-8',
        extra = 'ignore',
        case_sensitive = False,
    )

    @property
    def rabbitmq_url(self):
        return (
            f'amqp://{self.rabbit_login}:{self.rabbit_pass}'
            f'@{self.rabbit_host}:{self.rabbit_port}'
        )
    

rabbit_settings = RabbitMQSettings()

sendler_settings = SendlerSettings() # type: ignore