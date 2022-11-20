## NOTICE should run before start:
1. In order to create CA
   1. `cd .\source\`
   2. `& 'C:\Program Files\Git\usr\bin\openssl.exe' req -x509 -nodes -new -sha256 -days 1024 -newkey rsa:2048 -keyout RootCA.key -out RootCA.pem -subj "/C=US/CN=Example-Root-CA"`
   3. `& 'C:\Program Files\Git\usr\bin\openssl.exe' x509 -outform pem -in RootCA.pem -out RootCA.crt`
2. The docker-compose envs:
   1.env.mysql ```MYSQL_ROOT_PASSWORD=123456
MYSQL_DATABASE=cyber_proj
MYSQL_USER=cyber_user
MYSQL_PASSWORD=123456
MYSQL_ROOT_HOST=%```
   2.env.application ```DJANGO_SECRET_KEY=3d305kajG5Jy8KBafCMpHwDIsNi0SqVaW
DJANGO_DATABASE=docker
IS_PRODUCTION=1
DEBUG=0
EMAIL_HOST=smtp```

3. Log in docker is under `/app/source/debug.log` 
4. Password length is determined IN `AUTH_PASSWORD_VALIDATORS -> UserAttributeSimilarityValidator -> OPTIONS -> min_length`
5. Blacklisted password should be in `blacklist_passwords.txt` all lower-cased!
6. Password hash is determined using `PASSWORD_HASHERS=` options is in https://docs.djangoproject.com/en/4.1/topics/auth/passwords/

7. password dict is from https://github.com/danielmiessler/SecLists/tree/aad07fff50ca37af2926de4d07ff670bf3416fbc/Passwords

 
## SQL INJECTION
- should change config `BWAPP` to `True`
- Use this text for example `' UNION  SELECT 1,2,name FROM sqlite_master --`
  - In `/accounts/customer/` should be under name
  - In `/accounts/sign-up/` should be under first name
  - In `/accounts/log-in/` should be under name

## ESS
- todo: config
- todo: how to simulate