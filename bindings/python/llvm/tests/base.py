import os.path
import unittest
import tempfile
import sys
import subprocess

from llvm.core.module import Module

POSSIBLE_TEST_BINARIES = [
    'libreadline.so.5',
    'libreadline.so.6',
]

POSSIBLE_TEST_BINARY_PATHS = [
    '/usr/lib/debug',
    '/lib',
    '/usr/lib',
    '/usr/local/lib',
    '/lib/i386-linux-gnu',
]

CLANG = "/home/andersg/dev/llvm/build/Debug+Asserts/bin/clang"  # XXXX

class TestBase(unittest.TestCase):
    def get_test_binary(self):
        """Helper to obtain a test binary for object file testing.

        FIXME Support additional, highly-likely targets or create one
        ourselves.
        """
        for d in POSSIBLE_TEST_BINARY_PATHS:
            for lib in POSSIBLE_TEST_BINARIES:
                path = os.path.join(d, lib)

                if os.path.exists(path):
                    return path

        raise Exception('No suitable test binaries available!')
    get_test_binary.__test__ = False

    def get_test_file(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_file")

    def get_test_bc(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "test.bc")

    def clang(self, src):
        F = tempfile.NamedTemporaryFile()
        p = subprocess.Popen([CLANG, "-c", "-xc", "-g", "-emit-llvm", "-o", F.name, "-"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        o,e = p.communicate(src)
        if e:
            print e
        return Module.from_bitcode_file(F.name)


class captured_stderr:
    def __init__(self):
        self.prev = None

    def __enter__(self):
        F = tempfile.NamedTemporaryFile()
        self.prev = os.dup(sys.stderr.fileno())
        os.dup2(F.fileno(), sys.stderr.fileno())
        # hax hax
        F.__class__.data=property(lambda s: file(s.name).read())
        return F

    def __exit__(self, exc_type, exc_value, traceback):
        os.dup2(self.prev, sys.stderr.fileno())
        os.close(self.prev)
