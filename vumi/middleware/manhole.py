# -*- test-case-name: vumi.middleware.tests.test_manhole -*-

from vumi.middleware import BaseMiddleware

from twisted.internet import reactor
from twisted.cred import portal
from twisted.conch import manhole_ssh, manhole_tap
from twisted.conch.checkers import SSHPublicKeyDatabase
from twisted.python.filepath import FilePath


class SSHPubKeyDatabase(SSHPublicKeyDatabase):
    """
    Checker for authorizing people against a list of `authorized_keys` files.
    If nothing is specified then it defaults to `authorized_keys` and
    `authorized_keys2` for the logged in user.
    """
    def __init__(self, authorized_keys):
        self.authorized_keys = authorized_keys

    def getAuthorizedKeysFiles(self, credentials):
        if self.authorized_keys is not None:
            return [FilePath(ak) for ak in self.authorized_keys]

        return SSHPublicKeyDatabase.getAuthorizedKeysFiles(self, credentials)


class ManholeMiddleware(BaseMiddleware):
    """
    Middleware providing SSH access into the worker this middleware is attached
    to.

    Requires the following packages to be installed:

        * pyasn1
        * pycrypto


    :param int port:
        The port to open up. Defaults to `0` which has the reactor select
        any available port.
    :param list authorized_keys:
        List of absolute paths to `authorized_keys` files containing SSH public
        keys that are allowed access.
    """
    def validate_config(self):
        self.port = int(self.config.get('port', 0))
        self.authorized_keys = self.config.get('authorized_keys', None)

    def setup_middleware(self):
        self.validate_config()
        checker = SSHPubKeyDatabase(self.authorized_keys)
        ssh_realm = manhole_ssh.TerminalRealm()
        ssh_realm.chainedProtocolFactory = manhole_tap.chainedProtocolFactory({
            'worker': self.worker,
        })
        ssh_portal = portal.Portal(ssh_realm, [checker])
        ssh_factory = manhole_ssh.ConchFactory(ssh_portal)
        self.socket = reactor.listenTCP(self.port, ssh_factory)

    def teardown_middleware(self):
        self.socket.loseConnection()
