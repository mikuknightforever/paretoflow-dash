"""Validate one recorded experiment before any dashboard serves it.

This module only reads JSON and file hashes. It never imports a model runtime.
Select a complete experiment with PARETO_DATA_DIR before starting the server;
running servers keep their loaded records and must be restarted to switch runs.
"""
import hashlib
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_DIR = (ROOT / os.environ.get('PARETO_DATA_DIR', 'data')).resolve()


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def validate_bundle(data_dir):
    """Return manifest and trace only when they describe the same saved files."""
    directory = Path(data_dir)
    try:
        manifest = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
        trace = json.loads((directory / 'process_trace.json').read_text(encoding='utf-8'))
        if not isinstance(manifest, dict) or not isinstance(trace, dict):
            raise ValueError('manifest and trace must be JSON objects')
        if trace.get('schema_version') != 1:
            raise ValueError('unsupported recorded process trace schema')
        if not isinstance(trace.get('modes'), dict) or not trace['modes']:
            raise ValueError('recorded process trace has no configurations')
        if not isinstance(trace.get('directions'), list) or not trace['directions']:
            raise ValueError('recorded process trace has no directions')
        provenance = trace.get('provenance')
        if not isinstance(provenance, dict):
            raise ValueError('recorded process trace has no provenance')
        sample_hash = sha256(directory / 'sample.npz')
        checkpoint_hash = sha256(directory / 'checkpoints.pt')
        for label, recorded, actual in (
            ('manifest sample', manifest.get('sample_sha256'), sample_hash),
            ('trace sample', provenance.get('sample_sha256'), sample_hash),
            ('trace checkpoint', provenance.get('checkpoint_sha256'), checkpoint_hash),
        ):
            if recorded != actual:
                raise ValueError(f'{label} SHA-256 mismatch')
        if 'checkpoint_sha256' in manifest and manifest['checkpoint_sha256'] != checkpoint_hash:
            raise ValueError('manifest checkpoint SHA-256 mismatch')
    except (OSError, ValueError) as error:
        raise ValueError(
            f'Invalid recorded experiment at {directory}: {error}. '
            'Use a complete, validated sample/checkpoint/manifest/trace bundle; '
            'do not replace individual files in a running deployment.'
        ) from error
    return manifest, trace
