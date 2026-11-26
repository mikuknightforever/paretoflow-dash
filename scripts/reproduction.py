"""Publish a regenerated recording only after its complete bundle validates."""
from datetime import datetime, timezone
from pathlib import Path
import tempfile
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]


def default_output_dir():
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    return ROOT / 'runs' / f'{stamp}-{uuid4().hex[:8]}'


def write_text_atomic(path, content):
    """Replace one complete text file without sharing temporary names."""
    output = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8',
                                         prefix=f'.{output.name}-', suffix='.tmp',
                                         dir=output.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(content)
        temporary.replace(output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def build_bundle(output_dir, sample_builder, trace_builder, validator):
    """Keep the public destination absent until every generation check passes.

    The bundled historical fixture is never a valid generation destination.
    Dependencies are explicit so failure paths can be checked without training.
    Do not create or manipulate the chosen destination concurrently: portable
    directory rename cannot atomically reject a newly appeared empty directory
    on every platform. Existing completed (nonempty) runs cannot be replaced.
    """
    requested = Path(output_dir).expanduser()
    if requested.exists() or requested.is_symlink():
        raise FileExistsError(f'Refusing to overwrite an existing output: {requested}')
    destination = requested.resolve()
    fixture = (ROOT / 'data').resolve()
    if destination == fixture or fixture in destination.parents:
        raise ValueError('The bundled data directory is read-only for reproduction; choose a new run directory')
    if destination.exists():
        raise FileExistsError(f'Refusing to overwrite an existing output: {destination}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    # A sibling staging directory makes the final rename stay on one filesystem.
    with tempfile.TemporaryDirectory(prefix=f'.{destination.name}-', dir=destination.parent) as temporary:
        staged = Path(temporary) / 'bundle'
        staged.mkdir()
        sample_builder(staged)
        trace_builder(staged)
        validator(staged)
        # Reject destinations observed during generation; callers must not
        # manage this path concurrently with the final directory rename.
        if destination.exists():
            raise FileExistsError(f'Output appeared during generation: {destination}')
        staged.rename(destination)
    return destination
