from pydantic_settings import BaseSettings, SettingsConfigDict


#class configurator for checker's DB
class DatabaseSettings(BaseSettings):
    database_pass: str = 'postgres'
    database_user: str = 'postgres'
    database_host: str = 'db'
    database_host_dev: str = 'localhost'
    database_port: int = 5432
    database_port_dev: int = 5433
    database_name: str = 'CHECKER'


    model_config = SettingsConfigDict(
        env_file = 'checker.env',
        env_file_encoding = 'utf-8',
        extra = 'ignore',
        pyproject_toml_depth=2,
        case_sensitive = False,
    )


    @property
    def database_url(self):
        return (
            f'postgresql+asyncpg://{self.database_user}:{self.database_pass}'
            f'@{self.database_host}:{self.database_port}/{self.database_name}'
        )
    
    @property
    def database_url_to_host(self):
        return (
            f'postgresql+asyncpg://{self.database_user}:{self.database_pass}'
            f'@{self.database_host_dev}:{self.database_port}/{self.database_name}'
        )


#class configurator for checker's rabbit broker
class RabbitMQSettings(BaseSettings):
    rabbit_pass: str = 'guest'
    rabbit_login: str = 'guest'
    rabbit_host: str = 'rabbit'
    rabbit_port: int = 5672


    model_config = SettingsConfigDict(
        env_file = 'checker.env',
        env_file_encoding = 'utf-8',
        extra = 'ignore',
        pyproject_toml_depth=2,
        case_sensitive = False,
    )


    

    @property
    def rabbitmq_url(self):
        return (
            f'amqp://{self.rabbit_login}:{self.rabbit_pass}'
            f'@{self.rabbit_host}:{self.rabbit_port}'
        )
    

database_settings = DatabaseSettings() 

rabbit_settings = RabbitMQSettings() 