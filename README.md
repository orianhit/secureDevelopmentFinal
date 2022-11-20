## NOTICE should run before start:
1. `docker network create external-net`
2. `docker run -p 1025:1025 -p 1080:1080 msztolcman/sendria:v2.2.2.0`
3. in order to create CA
   1. `cd .\source\`
   2. `& 'C:\Program Files\Git\usr\bin\openssl.exe' req -x509 -nodes -new -sha256 -days 1024 -newkey rsa:2048 -keyout RootCA.key -out RootCA.pem -subj "/C=US/CN=Example-Root-CA"`
   3. `& 'C:\Program Files\Git\usr\bin\openssl.exe' x509 -outform pem -in RootCA.pem -out RootCA.crt`
4. for env create 2 files
   1. .env.mysql ```MYSQL_ROOT_PASSWORD=123456
MYSQL_DATABASE=cyber_proj
MYSQL_USER=cyber_user
MYSQL_PASSWORD=123456
MYSQL_ROOT_HOST=%```
   2. .env.application ```DJANGO_SECRET_KEY=3d305kajG5Jy8KBafCMpHwDIsNi0SqVaW
DJANGO_DATABASE=docker
IS_PRODUCTION=1
DEBUG=0
EMAIL_HOST=smtp```

5. password length is determined IN `AUTH_PASSWORD_VALIDATORS -> UserAttributeSimilarityValidator -> OPTIONS -> min_length`
6. blacklisted password should be in `blacklist_passwords.txt` all lower-cased!
7. password hash is determined using `PASSWORD_HASHERS=` options is in https://docs.djangoproject.com/en/4.1/topics/auth/passwords/

8. password dict is from https://github.com/danielmiessler/SecLists/tree/aad07fff50ca37af2926de4d07ff670bf3416fbc/Passwords
