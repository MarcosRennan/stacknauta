"""A05/A07: somente fixtures locais e falhas controladas, sem origens reais."""
import os
import signal
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import test_updates as fixtures
import atualizacoes
from atualizacoes import read_bytes, write_bytes, tree, load, atomic_json, move, sync_tree
from stacknauta_core import BootstrapError


class MaintenanceRecoveryTests(unittest.TestCase):
    setUp = fixtures.UpdateTests.setUp
    change = fixtures.UpdateTests.change
    plan = fixtures.UpdateTests.plan
    apply = fixtures.UpdateTests.apply

    def test_candidate_files_are_synced_before_first_promotion(self):
        self.change(); plan = self.plan()
        candidate = self.engine.session(plan['session_id'])/'candidate/Skills'
        expected = {(p.stat().st_dev, p.stat().st_ino) for p in candidate.rglob('*') if p.is_file()}
        synced = set()
        fsync, move = os.fsync, atualizacoes.move
        def record(fd):
            info = os.fstat(fd)
            if stat.S_ISREG(info.st_mode): synced.add((info.st_dev, info.st_ino))
            return fsync(fd)
        def promote(source, destination):
            self.assertTrue(expected <= synced, 'Dados candidatos não sincronizados antes da promoção')
            return move(source, destination)
        with patch.object(atualizacoes.os, 'fsync', side_effect=record), patch.object(atualizacoes, 'move', side_effect=promote):
            self.apply(plan)

    def test_leaf_replaced_after_inspection_is_never_followed(self):
        path = self.base/'race'; path.write_bytes(b'inside')
        outside = self.base/'outside'; outside.write_bytes(b'outside')
        original = atualizacoes.safe
        def race(root, relative):
            result = original(root, relative)
            if relative == 'race':
                path.unlink(); path.symlink_to(outside)
            return result
        with patch.object(atualizacoes, 'safe', side_effect=race):
            with self.assertRaises((ValueError, OSError)):
                read_bytes(self.base, 'race')
        self.assertEqual(outside.read_bytes(), b'outside')

    def test_sync_failure_before_promotion_preserves_active(self):
        self.change(); plan = self.plan()
        with patch.object(atualizacoes, 'sync_tree', side_effect=OSError('injected fsync failure')):
            with self.assertRaisesRegex(OSError, 'fsync'): self.apply(plan)
        self.assertEqual(tree(self.root/'Skills'), self.before)
        self.assertEqual(load(self.engine.session(plan['session_id']), 'journal.json')['phase'], 'prepared')

    def test_preparation_write_failure_never_seals_prepared_journal(self):
        self.change(); original = atualizacoes.write_bytes
        def fail(root, relative, data, *args, **kwargs):
            if relative == 'Skills/fontes.lock.json' and not kwargs.get('exclusive'):
                raise OSError('injected candidate write failure')
            return original(root, relative, data, *args, **kwargs)
        with patch.object(atualizacoes, 'write_bytes', side_effect=fail):
            result = self.engine.prepare({'fastapi'})
        self.assertEqual(result['status'], 'bloqueado')
        self.assertFalse((self.engine.session(result['session_id'])/'journal.json').exists())
        self.assertEqual(tree(self.root/'Skills'), self.before)

    def test_post_promotion_sync_failure_rolls_back_and_can_prepare_again(self):
        self.change(); plan = self.plan(); sync = atualizacoes.sync_tree
        def fail(root, expected=None):
            if root == self.root/'Skills' and expected == plan['candidate_tree']:
                raise OSError('injected post-promotion fsync failure')
            return sync(root, expected)
        with patch.object(atualizacoes, 'sync_tree', side_effect=fail):
            with self.assertRaisesRegex(OSError, 'post-promotion'): self.apply(plan)
        self.assertEqual(tree(self.root/'Skills'), self.before)
        self.assertEqual(load(self.engine.session(plan['session_id']), 'journal.json')['phase'], 'rolled_back')
        replacement = self.plan()
        self.assertEqual(self.apply(replacement)['status'], 'aplicado')

    def test_committed_is_recorded_after_active_file_and_directory_sync(self):
        self.change(); plan = self.plan(); sync, atomic = atualizacoes.sync_tree, atualizacoes.atomic_json
        synced = False
        def record(root, expected=None):
            nonlocal synced
            result = sync(root, expected)
            if root == self.root/'Skills' and expected == plan['candidate_tree']: synced = True
            return result
        def journal(path, value):
            if value.get('phase') == 'committed': self.assertTrue(synced)
            return atomic(path, value)
        with patch.object(atualizacoes, 'sync_tree', side_effect=record), patch.object(atualizacoes, 'atomic_json', side_effect=journal):
            result = self.apply(plan)
        self.assertTrue(Path(result['backup']).is_dir())

    def interrupted_state(self, *, published):
        self.change(); plan = self.plan(); session = self.engine.session(plan['session_id'])
        move(self.root/'Skills', session/'previous-Skills')
        if published: move(session/'candidate/Skills', self.root/'Skills')
        atomic_json(session/'journal.json', {'phase':'old_moved', 'plan_id':plan['plan_id']})
        return plan, session

    def test_interruption_before_publication_recovers_legacy_journal(self):
        plan, session = self.interrupted_state(published=False)
        self.assertEqual(self.engine.recover(plan['session_id'], approve=True)['status'], 'restaurado')
        self.assertEqual(tree(self.root/'Skills'), self.before)
        self.assertEqual(self.engine.recover(plan['session_id'], approve=True)['status'], 'restaurado')

    def test_interruption_after_publication_before_journal_completion_recovers(self):
        plan, session = self.interrupted_state(published=True)
        self.engine.recover(plan['session_id'], approve=True)
        self.assertEqual(tree(self.root/'Skills'), self.before)
        self.assertTrue(any(session.glob('failed-Skills-*')))

    def test_missing_backup_with_new_active_is_not_accepted(self):
        plan, session = self.interrupted_state(published=True)
        move(session/'previous-Skills', session/'preserved-backup')
        before = tree(self.root/'Skills')
        with self.assertRaisesRegex(ValueError, 'sem backup'):
            self.engine.recover(plan['session_id'], approve=True)
        self.assertEqual(tree(self.root/'Skills'), before)
        self.assertEqual(load(session, 'journal.json')['phase'], 'old_moved')

    def test_missing_backup_and_active_blocks_with_controlled_diagnostic(self):
        plan, session = self.interrupted_state(published=False)
        move(session/'previous-Skills', session/'preserved-backup')
        with self.assertRaisesRegex(ValueError, 'sem backup e biblioteca ativa'):
            self.engine.recover(plan['session_id'], approve=True)
        self.assertTrue((session/'preserved-backup').is_dir())

    def test_error_after_commit_record_does_not_report_success(self):
        self.change(); plan=self.plan(); atomic=atualizacoes.atomic_json
        def fail(path, value):
            result=atomic(path,value)
            if value.get('phase')=='committed': raise OSError('injected journal sync failure')
            return result
        with patch.object(atualizacoes,'atomic_json',side_effect=fail):
            with self.assertRaisesRegex(OSError,'journal sync'):self.apply(plan)
        self.assertEqual(tree(self.root/'Skills'),self.before)
        self.assertEqual(load(self.engine.session(plan['session_id']),'journal.json')['phase'],'rolled_back')

    def test_tampered_backup_is_preserved_and_recovery_refused(self):
        plan, session = self.interrupted_state(published=True)
        (session/'previous-Skills/Backend/fastapi/LICENSE').write_bytes(b'tampered')
        before = tree(self.root/'Skills')
        with self.assertRaisesRegex(ValueError, 'Backup alterado'):
            self.engine.recover(plan['session_id'], approve=True)
        self.assertEqual(tree(self.root/'Skills'), before)
        self.assertEqual((session/'previous-Skills/Backend/fastapi/LICENSE').read_bytes(), b'tampered')

    def test_unknown_journal_phase_blocks_without_mutation(self):
        self.change(); plan = self.plan(); session = self.engine.session(plan['session_id'])
        atomic_json(session/'journal.json', {'phase':'unknown', 'plan_id':plan['plan_id']})
        with self.assertRaisesRegex(ValueError, 'Diário inconsistente'):
            self.engine.recover(plan['session_id'], approve=True)
        self.assertEqual(tree(self.root/'Skills'), self.before)

    def test_script_checks_use_safe_bytes_and_preserve_module_type(self):
        candidate = self.base/'scripts'; folder=candidate/'Skills/Backend/fixture'; folder.mkdir(parents=True)
        (folder/'package.json').write_text('{"type":"module"}')
        relative='Skills/Backend/fixture/helper.js'
        data=b'export const value = 1; throw new Error("must not execute");\n'
        (candidate/relative).write_bytes(data)
        self.engine.check_changed_scripts(candidate,{relative:data},{})
        (folder/'helper.cjs').write_bytes(data)
        with self.assertRaisesRegex(ValueError,'Sintaxe'):
            self.engine.check_changed_scripts(candidate,{'Skills/Backend/fixture/helper.cjs':data},{})


class MaintenanceFilesystemTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='stacknauta-a07-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.file = self.root/'regular'; self.file.write_bytes(b'original')
        self.outside = self.root/'outside'; self.outside.mkdir()
        (self.outside/'sentinel').write_bytes(b'untouched')

    def test_regular_read_write_and_synchronization(self):
        write_bytes(self.root, 'nested/file', b'new')
        self.assertEqual(read_bytes(self.root, 'nested/file'), b'new')
        sync_tree(self.root)

    def test_final_symlink_is_rejected_for_read_write_and_metadata(self):
        (self.root/'link').symlink_to(self.outside/'sentinel')
        for action in (lambda:read_bytes(self.root,'link'), lambda:write_bytes(self.root,'link',b'bad'), lambda:atomic_json(self.root/'link',{})):
            with self.assertRaises((ValueError, OSError, BootstrapError)): action()
        self.assertEqual((self.outside/'sentinel').read_bytes(), b'untouched')

    def test_intermediate_symlink_is_rejected(self):
        (self.root/'link').symlink_to(self.outside, target_is_directory=True)
        for action in (lambda:read_bytes(self.root,'link/sentinel'), lambda:write_bytes(self.root,'link/sentinel',b'bad')):
            with self.assertRaises((ValueError, OSError, BootstrapError)): action()

    def test_hardlink_is_rejected_without_truncating_other_name(self):
        os.link(self.outside/'sentinel', self.root/'hardlink')
        for action in (lambda:read_bytes(self.root,'hardlink'), lambda:write_bytes(self.root,'hardlink',b'bad'), lambda:atomic_json(self.root/'hardlink',{})):
            with self.assertRaises(ValueError): action()
        self.assertEqual((self.outside/'sentinel').read_bytes(), b'untouched')

    def test_fifo_does_not_block(self):
        os.mkfifo(self.root/'fifo')
        def timeout(*_): raise AssertionError('Operação bloqueou no FIFO')
        previous = signal.signal(signal.SIGALRM, timeout); signal.alarm(2)
        try:
            for action in (lambda:read_bytes(self.root,'fifo'), lambda:write_bytes(self.root,'fifo',b'bad'), lambda:atomic_json(self.root/'fifo',{})):
                with self.assertRaises((ValueError, OSError)): action()
        finally: signal.alarm(0); signal.signal(signal.SIGALRM, previous)

    def test_directory_in_place_of_file_is_rejected(self):
        with self.assertRaises((ValueError, OSError)): read_bytes(self.root,'outside')
        with self.assertRaises((ValueError, OSError)): write_bytes(self.root,'outside',b'bad')

    def test_write_race_to_symlink_cannot_change_outside_file(self):
        original = atualizacoes.safe
        def race(root, relative):
            result = original(root, relative)
            if relative == 'regular':
                self.file.unlink(); self.file.symlink_to(self.outside/'sentinel')
            return result
        with patch.object(atualizacoes, 'safe', side_effect=race):
            with self.assertRaises((ValueError, OSError)): write_bytes(self.root,'regular',b'bad')
        self.assertEqual((self.outside/'sentinel').read_bytes(), b'untouched')

    def test_intermediate_replacement_after_inspection_is_not_followed(self):
        folder = self.root/'folder'; folder.mkdir(); (folder/'sentinel').write_bytes(b'inside')
        original = atualizacoes.safe
        def race(root, relative):
            result = original(root, relative)
            if relative == 'folder/sentinel':
                folder.rename(self.root/'preserved-folder'); folder.symlink_to(self.outside, target_is_directory=True)
            return result
        with patch.object(atualizacoes, 'safe', side_effect=race):
            with self.assertRaises((ValueError, OSError)): read_bytes(self.root, 'folder/sentinel')

    def test_escape_paths_are_rejected(self):
        for path in ('../outside/sentinel', '/tmp/outside', '.', 'a/../regular', '.git/config'):
            with self.subTest(path=path), self.assertRaises(ValueError): write_bytes(self.root,path,b'bad')

    def test_permission_errors_remain_controlled(self):
        original = os.open
        def denied(path, *args, **kwargs):
            if path == 'regular': raise PermissionError('injected EACCES')
            return original(path, *args, **kwargs)
        with patch.object(atualizacoes.os, 'open', side_effect=denied):
            with self.assertRaises(PermissionError): read_bytes(self.root,'regular')

    def test_destination_created_during_rename_is_preserved(self):
        source = self.root/'source'; source.mkdir(); (source/'data').write_bytes(b'original')
        destination = self.root/'destination'
        original = atualizacoes.rename_noreplace
        def race(*args, **kwargs):
            destination.mkdir()
            return original(*args, **kwargs)
        with patch.object(atualizacoes, 'rename_noreplace', side_effect=race):
            with self.assertRaises(ValueError): move(source,destination)
        self.assertEqual((source/'data').read_bytes(), b'original')
        self.assertEqual(list(destination.iterdir()), [])

    def test_tree_rejects_special_entries(self):
        (self.root/'link').symlink_to(self.outside/'sentinel')
        with self.assertRaises(ValueError): tree(self.root)

    def test_metadata_temporary_substituted_at_replace_is_detected(self):
        replace = os.replace
        def race(source, destination, **kwargs):
            temporary=self.root/source
            temporary.rename(self.root/'preserved-own-inode')
            temporary.symlink_to(self.outside/'sentinel')
            return replace(source,destination,**kwargs)
        with patch.object(atualizacoes.os,'replace',side_effect=race):
            with self.assertRaisesRegex(ValueError,'substituído'):
                atomic_json(self.root/'journal.json',{'phase':'prepared'})
        self.assertEqual((self.outside/'sentinel').read_bytes(),b'untouched')
        self.assertTrue((self.root/'preserved-own-inode').exists())
