## NOTICE should run before start:
1. In order to create CA, run this commands in git bash
   1. `cd .\source\`
   2. `openssl req -x509 -nodes -new -sha256 -days 1024 -newkey rsa:2048 -keyout RootCA.key -out RootCA.pem -subj "/C=US/CN=Example-Root-CA"`
   3. `openssl x509 -outform pem -in RootCA.pem -out RootCA.crt`
2. create files with this content (docker-compose envs):
   1. env for mysql
      1. file_name: `.env.mysql`
      2. content: 
```ini
MYSQL_ROOT_PASSWORD=123456
MYSQL_DATABASE=cyber_proj
MYSQL_USER=cyber_user
MYSQL_PASSWORD=123456
MYSQL_ROOT_HOST=%
```
   2. env for application
      1. file_name: `.env.application`
      2. content: 
```ini
DJANGO_SECRET_KEY=3d305kajG5Jy8KBafCMpHwDIsNi0SqVaW
IS_PRODUCTION=1
DEBUG=0
EMAIL_HOST=smtp
```

3. logs inside docker is written to file in this path `/app/source/debug.log` 
4. Password length is determined IN `AUTH_PASSWORD_VALIDATORS -> UserAttributeSimilarityValidator -> OPTIONS -> min_length`
5. Blacklisted password should be in `blacklist_passwords.txt` all lower-cased!
6. Password hash is determined using `PASSWORD_HASHERS=` options is in https://docs.djangoproject.com/en/4.1/topics/auth/passwords/

7. password dict is from https://github.com/danielmiessler/SecLists/tree/aad07fff50ca37af2926de4d07ff670bf3416fbc/Passwords

 
## SQL INJECTION
- should change config `BWAPP_SQLI` to `True`
- Use this texts for example:
   - sqlite3: `' UNION  SELECT 1,2,name FROM sqlite_master --`
   - mysql (docker): `' UNION SELECT 1,2,TABLE_NAME FROM information_schema.TABLES #`
- In thos urls:
  - In `/accounts/customer/` should be under name
  - In `/accounts/sign-up/` should be under first name
  - In `/accounts/log-in/` should be under name

## ESS
- should change config `BWAPP_XSS` to `True`
- Use this text for example `<script>alert('XSS');</script>`
  - In `/accounts/customer/` should be under name