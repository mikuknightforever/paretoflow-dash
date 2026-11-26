"""Reject mixed experiments before serving any of their dashboards."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from recorded_data import ROOT, sha256, validate_bundle
from process_view import load_trace


class RecordedBundleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        (self.directory / 'sample.npz').write_bytes(b'original sample')
        (self.directory / 'checkpoints.pt').write_bytes(b'original checkpoint')
        self.manifest = {'sample_sha256': sha256(self.directory / 'sample.npz')}
        self.trace = {
            'schema_version': 1, 'directions': [0], 'modes': {'guided': {}},
            'provenance': {
                'sample_sha256': self.manifest['sample_sha256'],
                'checkpoint_sha256': sha256(self.directory / 'checkpoints.pt'),
            },
        }
        self.write_metadata()
        load_trace.cache_clear()
        self.addCleanup(load_trace.cache_clear)

    def write_metadata(self):
        for name, value in [('manifest.json', self.manifest), ('process_trace.json', self.trace)]:
            (self.directory / name).write_text(json.dumps(value), encoding='utf-8')

    def test_matching_bundle_loads_without_model_runtime(self):
        self.assertEqual(validate_bundle(self.directory), (self.manifest, self.trace))
        self.assertEqual(load_trace(self.directory / 'process_trace.json'), self.trace)

    def test_regenerated_sample_and_manifest_cannot_reuse_old_trace(self):
        (self.directory / 'sample.npz').write_bytes(b'new sample')
        self.manifest['sample_sha256'] = sha256(self.directory / 'sample.npz')
        self.write_metadata()
        with self.assertRaisesRegex(ValueError, 'trace sample SHA-256 mismatch'):
            load_trace(self.directory / 'process_trace.json')

    def test_replaced_checkpoint_is_rejected(self):
        (self.directory / 'checkpoints.pt').write_bytes(b'new checkpoint')
        with self.assertRaisesRegex(ValueError, 'trace checkpoint SHA-256 mismatch'):
            validate_bundle(self.directory)

    def test_stale_manifest_is_rejected(self):
        self.manifest['sample_sha256'] = 'wrong'
        self.write_metadata()
        with self.assertRaisesRegex(ValueError, 'manifest sample SHA-256 mismatch'):
            validate_bundle(self.directory)

    def test_partial_bundle_is_rejected(self):
        for name in ('sample.npz', 'checkpoints.pt', 'manifest.json', 'process_trace.json'):
            with self.subTest(missing=name):
                path = self.directory / name
                content = path.read_bytes()
                path.unlink()
                try:
                    with self.assertRaisesRegex(ValueError, 'Invalid recorded experiment'):
                        validate_bundle(self.directory)
                finally:
                    path.write_bytes(content)

    def test_missing_provenance_is_rejected(self):
        self.trace.pop('provenance')
        self.write_metadata()
        with self.assertRaisesRegex(ValueError, 'no provenance'):
            validate_bundle(self.directory)

    def test_server_startup_rejects_mixed_bundle_before_loading_arrays(self):
        (self.directory / 'sample.npz').write_bytes(b'new sample')
        self.manifest['sample_sha256'] = sha256(self.directory / 'sample.npz')
        self.write_metadata()
        environment = dict(os.environ, PARETO_DATA_DIR=str(self.directory))
        result = subprocess.run(
            [sys.executable, '-B', '-c', 'import app'], cwd=ROOT, env=environment,
            capture_output=True, text=True, timeout=30,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('trace sample SHA-256 mismatch', result.stderr)
        self.assertNotIn('Cannot load file containing pickled data', result.stderr)

    def test_bundled_reference_still_validates(self):
        manifest, trace = validate_bundle(ROOT / 'data')
        self.assertEqual(manifest['sample_sha256'], trace['provenance']['sample_sha256'])


if __name__ == '__main__':
    unittest.main()
