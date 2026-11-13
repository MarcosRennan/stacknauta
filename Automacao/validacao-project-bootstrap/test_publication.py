"""A06: interrupções de processos filhos apenas em arquivos sintéticos temporários."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from stacknauta_core.filesystem import directory, publish, fingerprint
from stacknauta_core import BootstrapError


class PublicationRecoveryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='stacknauta-a06-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def interrupted(self, *, after_link):
        pid = os.fork()
        if pid == 0:
            link = os.link
            def interrupt(*args, **kwargs):
                link(*args, **kwargs)
                os._exit(73)
            with directory(self.root) as root:
                if after_link:
                    with patch('stacknauta_core.filesystem.os.link', side_effect=interrupt):
                        publish(root, 'item', b'original')
                else:
                    publish(root, 'item', b'original', hook=lambda _: os._exit(73))
            os._exit(1)
        _, status = os.waitpid(pid, 0)
        self.assertEqual(os.waitstatus_to_exitcode(status), 73)

    def test_interruption_after_link_leaves_one_link_and_can_resume(self):
        self.interrupted(after_link=True)
        with directory(self.root) as root:
            self.assertEqual(fingerprint(root, 'item')['size'], 8)
            publish(root, 'item', b'original')
        self.assertEqual((self.root/'item').stat().st_nlink, 1)

    def test_interruption_before_link_leaves_no_named_temporary(self):
        self.interrupted(after_link=False)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_normal_publication_has_one_name_and_complete_content(self):
        with directory(self.root) as root: publish(root, 'item', b'original')
        self.assertEqual((self.root/'item').read_bytes(), b'original')
        self.assertEqual((self.root/'item').stat().st_nlink, 1)
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ['item'])

    def test_own_anonymous_inode_and_content_match_final(self):
        link = os.link
        def check(source, name, **kwargs):
            fd = int(Path(source).name)
            info = os.fstat(fd)
            self.assertEqual(info.st_nlink, 0)
            self.assertEqual(Path(source).read_bytes(), b'original')
            self.assertEqual(list(self.root.iterdir()), [])
            link(source, name, **kwargs)
            final = (self.root/'item').stat()
            self.assertEqual((info.st_dev, info.st_ino), (final.st_dev, final.st_ino))
            self.assertEqual(final.st_nlink, 1)
        with directory(self.root) as root, patch('stacknauta_core.filesystem.os.link', side_effect=check):
            publish(root, 'item', b'original')

    def test_reexecution_preserves_final_bytes_inode_mode_and_timestamps(self):
        self.interrupted(after_link=True)
        path = self.root/'item'; before = path.stat()
        with directory(self.root) as root:
            publish(root, 'item', b'original'); publish(root, 'item', b'original')
        after = path.stat()
        self.assertEqual(path.read_bytes(), b'original')
        self.assertEqual((before.st_ino,before.st_mode,before.st_mtime_ns,before.st_ctime_ns),
                         (after.st_ino,after.st_mode,after.st_mtime_ns,after.st_ctime_ns))

    def test_unknown_temporary_with_same_prefix_is_not_deleted(self):
        path = self.root/'.stacknauta-tmp-unknown'; path.write_bytes(b'different')
        with directory(self.root) as root: publish(root,'item',b'original')
        self.assertEqual(path.read_bytes(),b'different')

    def test_temporary_from_other_operation_is_not_deleted(self):
        path = self.root/'.stacknauta-tmp-other'; path.write_bytes(b'original')
        with directory(self.root) as root: publish(root,'item',b'original')
        self.assertEqual(path.read_bytes(),b'original')
        self.assertNotEqual(path.stat().st_ino,(self.root/'item').stat().st_ino)

    def test_temporary_symlink_is_preserved_and_not_followed(self):
        outside = self.root/'sentinel'; outside.write_bytes(b'untouched')
        path = self.root/'.stacknauta-tmp-symlink'; path.symlink_to(outside)
        with directory(self.root) as root: publish(root,'item',b'original')
        self.assertTrue(path.is_symlink())
        self.assertEqual(outside.read_bytes(),b'untouched')

    def test_tampered_final_is_never_replaced(self):
        (self.root/'item').write_bytes(b'tampered')
        with directory(self.root) as root, self.assertRaises(BootstrapError):
            publish(root,'item',b'original')
        self.assertEqual((self.root/'item').read_bytes(),b'tampered')

    def test_legacy_hardlink_without_operation_evidence_blocks_and_is_preserved(self):
        temporary = self.root/'.stacknauta-tmp-legacy'; temporary.write_bytes(b'original')
        os.link(temporary, self.root/'item')
        with directory(self.root) as root, self.assertRaisesRegex(BootstrapError, 'hardlink perigoso'):
            publish(root,'item',b'original')
        self.assertEqual(temporary.stat().st_nlink,2)
        self.assertEqual((self.root/'item').read_bytes(),b'original')

    def test_unsupported_tmpfile_blocks_without_named_fallback(self):
        original = os.open
        def unsupported(path, flags, *args, **kwargs):
            if flags & os.O_TMPFILE == os.O_TMPFILE: raise OSError('O_TMPFILE unsupported')
            return original(path, flags, *args, **kwargs)
        with directory(self.root) as root, patch('stacknauta_core.filesystem.os.open',side_effect=unsupported):
            with self.assertRaisesRegex(OSError,'unsupported'):publish(root,'item',b'original')
        self.assertEqual(list(self.root.iterdir()),[])
