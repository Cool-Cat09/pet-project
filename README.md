this project is backend realisation of price parser from diff e-shops. 
when a price will be less than specified.

it consist of 3 microservices:
API - andles user requests, product subscriptions, and threshold settings.
Parser - scrapes, extracts and compare price data from target e-shops.
Notification - triggers alerts when price conditions are met.

to start just use "docker compose up".
settings are specified in ..._config files.
to make and run migrations switch urls in alembic's env files to dev version