# Secure Development Project

## should run before start:
1. In order to create CA, run this commands in git bash
   1. `cd .\source\`
   2. `openssl req -x509 -nodes -new -sha256 -days 1024 -newkey rsa:2048 -keyout RootCA.key -out RootCA.pem -subj "//C=US//CN=Example-Root-CA"`
   3. `openssl x509 -outform pem -in RootCA.pem -out RootCA.crt`
2. create files with this content (docker-compose envs) in your project root:
   1. env for mysql
      1. file_name: `.env.mysql`
      2. copy this content to the file mentioned above:
```ini
MYSQL_ROOT_PASSWORD=123456
MYSQL_DATABASE=cyber_proj
MYSQL_USER=cyber_user
MYSQL_PASSWORD=123456
MYSQL_ROOT_HOST=%
```
   2. env for application
        1. file_name: `.env.application`
        2. copy this content to the file mentioned above:
```ini
DJANGO_SECRET_KEY=3d305kajG5Jy8KBafCMpHwDIsNi0SqVaW
IS_PRODUCTION=1
DEBUG=0
EMAIL_HOST_PASSWORD='sltwurlffnlknzxd'
EMAIL_HOST_USER=securedevelopmentfinal@gmail.com
```

## How to start docker compose
```bash
docker-compose up
```
and then open `https://127.0.0.1:9000` in your browser

## Known Passwords
- 10_million_password_list_top_100000.txt from `https://github.com/wikimedia/common-passwords`
- 500-worst-passwords.txt from `https://github.com/danielmiessler/SecLists/tree/master/Passwords`
- xato-net-10-million-passwords-dup.txt from `https://github.com/danielmiessler/SecLists/tree/master/Passwords`

 
## SQL INJECTION
- should change config (`docker-compose.yaml`)`BWAPP_SQLI` to `True`
- implementation is in `source/accounts/views.py`
- Use this texts for example:
   - sqlite3 (local): `' UNION SELECT 1,2,name FROM sqlite_master --`
     - `' UNION SELECT 1,username,password FROM auth_user --`
   - mysql (docker): `' UNION SELECT 1,2,TABLE_NAME FROM information_schema.TABLES #`
     - - `' UNION SELECT 1,username,password FROM auth_user #`
- In those urls:
  - In `/accounts/customer/` should be under name
  - In `/accounts/sign-up/` should be under first name
  - In `/accounts/log-in/` should be under name
### Added functionality
- also you can change `BWAPP_PLAIN_TEXT` environ to `True` in order to save passwords as plain text  

## XSS
- should change config (`docker-compose.yaml`) `BWAPP_XSS` to `True`
- implemented in `source/accounts/context_processors.py` and `source/accounts/templates/accounts/customer_create.html`
- Use this text for example `<script>alert('XSS');</script>`
- In those urls:
  - In `/accounts/customer/` should be under name
### Added functionality
- also you can change `CORS_ORIGIN_ALLOW_ALL` environ to `True` in order to allow XSS to other hosts.

## Config
- Password length is determined IN `AUTH_PASSWORD_VALIDATORS -> UserAttributeSimilarityValidator -> OPTIONS -> min_length`
- Complex password is determined IN `AUTH_PASSWORD_VALIDATORS -> PasswordCharacterValidator -> OPTIONS`
- Password History (reuse password forbidden) IN `AUTH_PASSWORD_VALIDATORS -> UniquePasswordsValidator -> OPTIONS -> last_passwords`
- Password Forbidden list file path IN `AUTH_PASSWORD_VALIDATORS -> CommonPasswordValidator -> OPTIONS -> password_list_path`
  - Blacklisted password list should be in `blacklist_passwords.txt` all lower-cased!
- Logging in retries before block config IN `AXES_FAILURE_LIMIT` and blocking only by username (not ip) IN `AXES_ONLY_USER_FAILURES`
- Password hash is determined using `PASSWORD_HASHERS=` we implemented 2 custom hashers (sha1 and plaintext) in `source/accounts/hashers.py` which can be swapped via `BWAPP_PLAIN_TEXT` environment variable
- logs inside docker is written to file in this path `/app/source/debug.log`
- SHA1 token for restore password email implemented at `source/accounts/tokens.py`
