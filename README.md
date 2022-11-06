## NOTICE:
1. password length is determined IN `AUTH_PASSWORD_VALIDATORS -> UserAttributeSimilarityValidator -> OPTIONS -> min_length`
2. blacklisted password should be in `blacklist_passwords.txt` all lower-cased!
3. password hash is determined using `PASSWORD_HASHERS=` options is in https://docs.djangoproject.com/en/4.1/topics/auth/passwords/


todo:
- add bad passwords dict from internet
- should be estatic (points will be given)