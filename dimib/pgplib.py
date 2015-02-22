from django.conf import settings
import gnupg


def initGPG ():
    return gnupg.GPG(gnupghome = settings.GPG_HOMEDIR)


def generateKey (username):
    gpg = initGPG()
    input_data = gpg.gen_key_input(
        key_type = 'RSA',
        name_real = username,
        name_email = '{0}@{1}'.format(username, settings.SITE_ADDRESS),
        expire_date = 0
    )
    key = gpg.gen_key(input_data)
    if key:
        private_key = gpg.export_keys(key.fingerprint, True)
        if not settings.DEBUG:
            gpg.delete_keys(key.fingerprint, True)
        return private_key
    return


def verify (user, data, signature):
    if data in signature:
        gpg = initGPG()
        verified = gpg.verify(signature)
        if verified.valid:
            return verified.username.split()[0] == user
    return False


