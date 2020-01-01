from hashlib import blake2b


def hash_with_blake2b(msg):
    h = blake2b(digest_size=20)
    h.update(bytes(msg, encoding='utf-8'))
    r = h.hexdigest()
    return r