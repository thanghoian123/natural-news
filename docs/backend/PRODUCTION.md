# VIP LOGIN BACKEND PRODUCTION

Things to do when going to production:

1. Setting Environment:

- set `env` parameter to `PRODUCTION`.

2. Changing Mail Server Config:

- current settings is my personal Gmail.
- settings in [config.py file](../../src/vip_login/config.py).

3. Changing CORS allowance to FrontEnd URL in [main.py file](../../src/vip_login/main.py)

4. Implement function `_get_llm_response` in [main.py file](../../src/vip_login/main.py) for actual llm response.

Feel free for changing docker compose file
