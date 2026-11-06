"""Python 2.7 regression tests; synthetic credentials, no service requests."""
import base64
import errno
import os
import pty
import select
import signal
import subprocess
import sys
import termios
import time
import unittest


class PasswordInputTests(unittest.TestCase):
    def session(self, password, interrupt=False):
        child = r'''
import base64, sys, urllib2
from StringIO import StringIO
def reply(request):
    expected = base64.b64encode('user@example.invalid:' + sys.argv[1])
    assert request.get_header('Authorization') == 'Basic ' + expected
    return StringIO('{}')
urllib2.urlopen = reply
namespace = {'__name__': 'password_test'}
execfile('push_zeo.py', namespace)
assert namespace['ZEO_USER'] == 'user@example.invalid'
assert namespace['ZEO_PASSWORD'] == sys.argv[1]
assert namespace['get_zeo']('2000-01-01') == {'data': [{'obj': {
    'id': '2000-01-01', 'date': '2000-01-01', 'record': {}}}]}
print('AUTH_OK')
'''
        pid, fd = pty.fork()
        if pid == 0:
            os.execl(sys.executable, sys.executable, '-c', child, password)
        output = ''
        status = None
        try:
            deadline = time.time() + 10
            sent_email = sent_password = False
            while time.time() < deadline:
                if select.select([fd], [], [], 0.1)[0]:
                    try:
                        chunk = os.read(fd, 4096)
                    except OSError as error:
                        if error.errno == errno.EIO:
                            break
                        raise
                    if not chunk:
                        break
                    output += chunk
                if not sent_email and 'Enter email\r\n>' in output:
                    os.write(fd, 'user@example.invalid\n')
                    sent_email = True
                if not sent_password and 'Enter password\r\n>' in output:
                    if interrupt:
                        os.write(fd, '\x03')
                    else:
                        os.write(fd, password + '\n')
                    sent_password = True
            else:
                self.fail('password prompt timed out')
            _, status = os.waitpid(pid, 0)
            self.assertTrue(termios.tcgetattr(fd)[3] & termios.ECHO)
            self.assertTrue(sent_password)
            self.assertNotIn(password, output)
            if interrupt:
                self.assertNotIn('AUTH_OK', output)
                self.assertNotEqual(status, 0)
            else:
                self.assertEqual(status, 0, output)
                self.assertIn('AUTH_OK', output)
        finally:
            if status is None:
                os.kill(pid, signal.SIGKILL)
                os.waitpid(pid, 0)
            os.close(fd)

    def test_password_hidden_and_auth_unchanged(self):
        self.session('synthetic-secret-4926')

    def test_spaces_and_punctuation_preserved(self):
        self.session('  synthetic : p@ss \\ value  ')

    def test_interrupt_restores_echo(self):
        self.session('never-entered-secret', interrupt=True)

    def test_no_terminal_aborts_before_fallback_read(self):
        child = r'''
import getpass
def forbidden_read(*args, **kwargs):
    raise AssertionError('unsafe fallback read attempted')
getpass._raw_input = forbidden_read
execfile('push_zeo.py', {'__name__': 'password_test'})
'''
        process = subprocess.Popen(
            [sys.executable, '-c', child], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            preexec_fn=os.setsid)
        out, err = process.communicate('user@example.invalid\n')
        self.assertNotEqual(process.returncode, 0)
        self.assertIn('Cannot hide password input', err)
        self.assertNotIn('unsafe fallback read attempted', err)


if __name__ == '__main__':
    unittest.main()
