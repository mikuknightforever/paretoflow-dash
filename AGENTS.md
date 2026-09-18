# Project working agreement

This agreement applies to `mikuknightforever/paretoflow-dash`, as requested by the repository owner on 2026-09-17.

- Automatic commits, direct pushes to main, and conversation-triggered daily branch catch-up follow the user's switchable global Codex policy. This file grants no independent automatic publishing authorization.
- Read the master setting with `git config --global --type=bool --get codex.mainSyncEnabled` and the repository opt-out separately with `git config --local --type=bool --get codex.mainSyncEnabled`. Automatic publication requires global `true` and no local `false` or invalid setting. Missing global settings mean disabled; missing local settings inherit. Global off always wins. Reread the switch before publishing.
- When enabled, use the global direct-main and next-day catch-up procedure with repository-local `codex.lastMainSyncDate` and `codex.lastMainSyncCommit`. When disabled, perform no automatic commit/merge/push; a specific user request to publish remains valid. Explicit task instructions take precedence.
- Run checks appropriate to the actual change before publishing. For Dash behavior changes, the normal regression command is `python -m unittest discover -s tests -v`. Reuse checks already passed for the unchanged code; documentation-only changes do not require rerunning model/data tests.
- Preserve unfinished/unrelated work, verify the remote main commit after pushing, and report what was published. Track synchronization metadata locally, not as daily commits in the repository.

## Current scope

The sample/trace regeneration consistency issue and the CUDA behavior of `scripts/build_sample.py` are explicitly deferred. Do not change those paths or regenerate experimental records without a new task to do so. The dashboards use bundled recorded results; ordinary viewing requires no training or model inference.
