from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    database_pass: str = 'postgres'
    database_user: str = 'postgres'
    database_host: str = 'db'
    database_host_dev: str = 'localhost'
    database_port: int = 5432
    database_port_dev: int = 5433
    database_name: str = 'API'


    model_config = SettingsConfigDict(
        env_file = 'api.env',
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
        """using to work with bd in manual mode"""
        return (
            f'postgresql+asyncpg://{self.database_user}:{self.database_pass}'
            f'@{self.database_host_dev}:{self.database_port}/{self.database_name}'
        )


class RabbitMQSettings(BaseSettings):
    rabbit_pass: str = 'guest'
    rabbit_login: str = 'guest'
    rabbit_host: str = 'rabbit'
    rabbit_host_to_dev: str = 'localhost'
    rabbit_port: int = 5672


    model_config = SettingsConfigDict(
        env_file = 'api.env',
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
    
    @property
    def rabbit_url_to_dev(self):
        return (
            f'amqp://{self.rabbit_login}:{self.rabbit_pass}'
            f'@{self.rabbit_host_to_dev}:{self.rabbit_port}'
        )
    

class JWT_Issuence_Settings(BaseSettings):
    private_key_path: str = 'private_key.pem'
    public_key_path: str = 'public_key.pem'
    algorithm: str = 'RS256'
    access_token_expire: int = 23
    refresh_token_expire: int = 43200


    model_config = SettingsConfigDict(
        env_file = 'api.env',
        env_file_encoding = 'utf-8',
        extra = 'ignore',
        case_sensitive = False,
    )




    @property
    def read_public_key(self):
        with open(self.public_key_path) as f:
            public_key = f.read()
        return public_key
    

    @property
    def read_private_key(self):
        with open(self.private_key_path) as f:
            private_key = f.read()
            return private_key


database_settings = DatabaseSettings() 

rabbit_settings = RabbitMQSettings() 

jwt_settings = JWT_Issuence_Settings()