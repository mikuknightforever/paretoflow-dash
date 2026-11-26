"""Exercise reproduction safety without training or importing the model runtime."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
import sys
import tempfile
from threading import Barrier
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.reproduction import build_bundle, default_output_dir, write_text_atomic


class ReproductionTests(unittest.TestCase):
    def test_atomic_trace_writers_use_distinct_temporary_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            output = directory / 'process_trace.json'
            output.write_text('previous recording', encoding='utf-8')
            ready = Barrier(2)
            staged = []
            replace = Path.replace

            def publish(source, destination):
                staged.append(source)
                self.assertEqual(source.parent, directory)
                self.assertIn(source.read_text(encoding='utf-8'), ('first complete trace', 'second complete trace'))
                ready.wait(timeout=5)
                return replace(source, destination)

            with patch.object(Path, 'replace', publish), ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(write_text_atomic, output, content)
                           for content in ('first complete trace', 'second complete trace')]
                for future in futures:
                    future.result(timeout=10)
            self.assertEqual(len(set(staged)), 2)
            self.assertIn(output.read_text(encoding='utf-8'), ('first complete trace', 'second complete trace'))
            self.assertEqual(list(directory.iterdir()), [output])

    def test_atomic_trace_write_failures_preserve_previous_file_and_cleanup(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            output = directory / 'process_trace.json'
            output.write_bytes(b'previous verified trace')
            # A failing write must not leave even an empty temporary behind.
            with self.assertRaises(TypeError):
                write_text_atomic(output, object())
            self.assertEqual(output.read_bytes(), b'previous verified trace')
            self.assertEqual(list(directory.iterdir()), [output])
            # A completed write whose final rename fails must also preserve it.
            with patch.object(Path, 'replace', side_effect=OSError('rename failed')):
                with self.assertRaisesRegex(OSError, 'rename failed'):
                    write_text_atomic(output, 'new complete trace')
            self.assertEqual(output.read_bytes(), b'previous verified trace')
            self.assertEqual(list(directory.iterdir()), [output])

    def test_existing_outputs_and_fixture_subdirectories_are_rejected_before_work(self):
        builders = [Mock(), Mock(), Mock()]
        with tempfile.TemporaryDirectory() as temporary:
            existing = Path(temporary) / 'existing'
            existing.mkdir()
            sentinel = existing / 'keep.txt'
            sentinel.write_text('original', encoding='utf-8')
            for path in (existing, sentinel, ROOT / 'data'):
                with self.subTest(path=path), self.assertRaises(FileExistsError):
                    build_bundle(path, *builders)
            with self.assertRaises(ValueError):
                build_bundle(ROOT / 'data' / 'new-reproduction', *builders)
            self.assertEqual(sentinel.read_text(encoding='utf-8'), 'original')
        for builder in builders:
            builder.assert_not_called()

    def test_complete_bundle_appears_only_after_trace_and_validation(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / 'result'
            calls = []

            def sample(directory):
                self.assertFalse(destination.exists())
                calls.append(('sample', directory))
                for name in ('sample.npz', 'checkpoints.pt', 'manifest.json'):
                    (directory / name).write_text(name, encoding='utf-8')

            def trace(directory):
                self.assertFalse(destination.exists())
                calls.append(('trace', directory))
                self.assertEqual((directory / 'sample.npz').read_text(), 'sample.npz')
                (directory / 'process_trace.json').write_text('validated replay', encoding='utf-8')

            def validate(directory):
                self.assertFalse(destination.exists())
                calls.append(('validate', directory))
                self.assertEqual((directory / 'process_trace.json').read_text(), 'validated replay')

            actual = build_bundle(destination, sample, trace, validate)
            self.assertEqual(actual, destination)
            self.assertEqual([name for name, _ in calls], ['sample', 'trace', 'validate'])
            self.assertEqual(len({directory for _, directory in calls}), 1)
            self.assertEqual({p.name for p in destination.iterdir()},
                             {'sample.npz', 'checkpoints.pt', 'manifest.json', 'process_trace.json'})
            self.assertEqual(list(Path(temporary).iterdir()), [destination])

    def test_generation_or_verification_failure_does_not_publish_partial_output(self):
        for failing_stage in ('sample', 'trace', 'validate'):
            with self.subTest(stage=failing_stage), tempfile.TemporaryDirectory() as temporary:
                parent = Path(temporary)
                original = parent / 'original-recording'
                original.mkdir()
                sentinel = original / 'sample.npz'
                sentinel.write_bytes(b'original recording')
                destination = parent / 'new-recording'
                called = []

                def stage(name):
                    def execute(directory):
                        called.append(name)
                        (directory / (name + '.partial')).write_text('partial', encoding='utf-8')
                        if name == failing_stage:
                            raise RuntimeError('reproduction check failed')
                    return execute

                with self.assertRaisesRegex(RuntimeError, 'reproduction check failed'):
                    build_bundle(destination, stage('sample'), stage('trace'), stage('validate'))
                self.assertEqual(called[-1], failing_stage)
                self.assertFalse(destination.exists())
                self.assertEqual(sentinel.read_bytes(), b'original recording')
                self.assertEqual(list(parent.iterdir()), [original])

    def test_output_created_during_generation_is_preserved(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / 'result'

            def concurrent_output(_):
                destination.mkdir()
                (destination / 'keep.txt').write_text('other writer', encoding='utf-8')

            with self.assertRaisesRegex(FileExistsError, 'appeared during generation'):
                build_bundle(destination, Mock(), Mock(), concurrent_output)
            self.assertEqual((destination / 'keep.txt').read_text(), 'other writer')
            self.assertEqual(list(Path(temporary).iterdir()), [destination])

    def test_default_run_destinations_are_unique_and_outside_fixture(self):
        first, second = default_output_dir(), default_output_dir()
        self.assertNotEqual(first, second)
        self.assertEqual(first.parent, ROOT / 'runs')
        self.assertFalse(first.exists())
        self.assertFalse(second.exists())

    def test_both_entry_points_disable_cuda_before_loading_model_libraries(self):
        # Fresh subprocesses model a CUDA-capable caller without requiring a GPU
        # or installing Torch in the web/test environment. The import hook fails
        # at the first model-library import if CPU selection was applied too late.
        program = r'''
import builtins, importlib, os, sys, types
os.environ['CUDA_VISIBLE_DEVICES'] = '0'
observed = []
numpy = types.ModuleType('numpy')
torch = types.ModuleType('torch')
torch.nn = types.SimpleNamespace(Module=object)
paretoflow = types.ModuleType('paretoflow')
for name in ('ParetoFlow', 'Task', 'FlowMatching', 'VectorFieldNet'):
    setattr(paretoflow, name, type(name, (), {}))
stubs = {'numpy':numpy, 'torch':torch, 'paretoflow':paretoflow}
real_import = builtins.__import__
def checked_import(name, *args, **kwargs):
    if name in stubs:
        assert os.environ.get('CUDA_VISIBLE_DEVICES') == '', name
        observed.append(name)
        return stubs[name]
    return real_import(name, *args, **kwargs)
builtins.__import__ = checked_import
importlib.import_module(sys.argv[1])
assert {'numpy','torch','paretoflow'}.issubset(observed), observed
print('CPU selected before model imports')
'''
        for module in ('scripts.build_sample', 'scripts.build_trace'):
            with self.subTest(module=module):
                result = subprocess.run([sys.executable, '-B', '-c', program, module],
                                        cwd=ROOT, capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn('CPU selected before model imports', result.stdout)


if __name__ == '__main__':
    unittest.main()
