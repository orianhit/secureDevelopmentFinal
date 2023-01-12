from django.conf import settings
import hashlib
from django.contrib.auth.hashers import BasePasswordHasher, mask_hash, must_update_salt
from django.utils.crypto import constant_time_compare


class CustomPasswordHasher(BasePasswordHasher):
    algorithm = "cstm" # custom password hasher
    iterations = 260000
    # digest = hashlib.sha256

    def encode(self, password, salt, iterations=None):
        assert password is not None
        assert salt and '$' not in salt
        iterations = iterations or self.iterations
        hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), iterations,  dklen=24)
        return "%s$%d$%s$%s" % (self.algorithm, iterations, salt, hash)

    def decode(self, encoded):
        algorithm, iterations, salt, hash = encoded.split('$', 3)
        assert algorithm == self.algorithm
        return {
            'algorithm': algorithm,
            'hash': hash,
            'iterations': int(iterations),
            'salt': salt,
        }

    def verify(self, password, encoded):
        decoded = self.decode(encoded)
        encoded_2 = self.encode(password, decoded['salt'], decoded['iterations'])
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        decoded = self.decode(encoded)
        return {
            _('algorithm'): decoded['algorithm'],
            _('iterations'): decoded['iterations'],
            _('salt'): mask_hash(decoded['salt']),
            _('hash'): mask_hash(decoded['hash']),
        }

    def must_update(self, encoded):
        decoded = self.decode(encoded)
        update_salt = must_update_salt(decoded['salt'], self.salt_entropy)
        return (decoded['iterations'] != self.iterations) or update_salt

    def harden_runtime(self, password, encoded):
        decoded = self.decode(encoded)
        extra_iterations = self.iterations - decoded['iterations']
        if extra_iterations > 0:
            self.encode(password, decoded['salt'], extra_iterations)


class BadPasswordHasher(BasePasswordHasher):
    algorithm = "no_algorithm"
    iterations = 0

    def encode(self, password, salt, iterations=None):
        assert password is not None
        iterations = iterations or self.iterations
        return "%s$%d$%s$%s" % (self.algorithm, iterations, salt, password)

    def decode(self, encoded):
        algorithm, iterations, salt, hash = encoded.split('$', 3)
        assert algorithm == self.algorithm
        return {
            'algorithm': algorithm,
            'hash': hash,
            'iterations': int(iterations),
            'salt': salt,
        }

    def verify(self, password, encoded):
        decoded = self.decode(encoded)
        encoded_2 = self.encode(password, decoded['salt'], decoded['iterations'])
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        decoded = self.decode(encoded)
        return {
            _('algorithm'): decoded['algorithm'],
            _('iterations'): decoded['iterations'],
            _('salt'): mask_hash(decoded['salt']),
            _('hash'): mask_hash(decoded['hash']),
        }

    def must_update(self, encoded):
        decoded = self.decode(encoded)
        update_salt = must_update_salt(decoded['salt'], self.salt_entropy)
        return (decoded['iterations'] != self.iterations) or update_salt

    def harden_runtime(self, password, encoded):
        decoded = self.decode(encoded)
        extra_iterations = self.iterations - decoded['iterations']
        if extra_iterations > 0:
            self.encode(password, decoded['salt'], extra_iterations)