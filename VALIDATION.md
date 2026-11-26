# Validation

## Repair verification — 2026-11-25

This repair starts from GitHub `main` at `7d167b3b22fcced691b61bfe8206d1c6dc23735d` and includes the previously local marker, label and narrow-screen layout fixes. The results below are local checks of the repair, not a statement that a hosted deployment has been updated.

- **83 tests pass with Dash 3.4.0** on Python 3.12.14, Plotly 6.9.0, NumPy 1.26.4 and Flask 3.1.3. `pip check` passes in this viewer environment.
- **83 tests pass with Dash 2.18.2** on Python 3.12.14, Plotly 6.9.0, NumPy 1.26.4 and Flask 3.0.3, using isolated compatibility packages without changing the default viewer environment. The process UI suite exercises 71 HTTP callbacks in each run.
- The two formerly failing Method tests now check that rejected clicks produce **no component updates**: HTTP 204 must have an empty body, while HTTP 200 must contain the exact empty Dash response envelope. Fresh clicks still have to select the correct record and design. A negative test rejects successful responses that actually change a component.
- An actual complete CPU run generated sample, checkpoint, manifest and matching trace in a new experiment directory. All three configurations passed exact archive, evaluated-objective, proxy-prediction and final-output comparisons, plus trace-on/off output and Torch/NumPy random-state checks. A subsequent standalone trace replay also passed after the unique temporary-file writer was added.
- The numerical run used Python 3.10.11, PyTorch 2.2.2+cpu, NumPy 1.24.4, SciPy 1.15.3, pymoo 0.6.1.3 and tqdm 4.66.2. These numerical versions are pinned in `requirements-reproduce.txt`; viewer dependencies are separate. No CUDA hardware run was performed. Subprocess regression tests verify that both reproduction entry points disable CUDA **before** importing model libraries.
- The generated bundle was selected with `PARETO_DATA_DIR` and successfully imported by the viewer. Ten startup/HTTP endpoints passed, and all 2,415 detailed direction archives matched its selected sample. The bundled historical sample and checkpoint retain their fixed hashes; the original data files were not replaced.
- Regression cases reject an updated sample/manifest paired with an old trace, a changed checkpoint, a stale manifest, missing provenance and missing bundle files. A subprocess confirms that server startup rejects a mismatched bundle before loading its arrays. Generation tests cover failure at each stage, existing-output protection, unique output directories and trace write/replace failures. Concurrent trace writers use distinct temporary files and only publish complete content.
- Focused browser checks covered Method C5 selection and full-record context, Process design/state plots, Neighbors K=5 selection, Guidance front switching and Explorer replay. The previous overlapping markers/labels and timeline overflow were checked in desktop and narrow layouts. At an observed 390 CSS-pixel width, the Process design/state plots remained 215px high and the checked pages had no document-level horizontal overflow. This was a focused check of the five affected modules, not a repeat of every state or device in the historical 14-module audit.
- GitHub Actions is configured for Python 3.10/3.12 with Dash 3.4.0/2.18.2, Node-based playback tests and dependency checks. The local results above do not imply that hosted Actions or the production deployment have already run this revision.

The default viewer now pins Dash 3.4.0 and Plotly 6.9.0. Reproduction publishes a fresh directory only after sample, checkpoint, manifest and exact-validated trace are complete; it never replaces the bundled fixture. The viewer validates matching file hashes at startup and uses one selected directory for all recorded-result panels. Switching experiments requires a server restart. The original sampler's documented undefined-angle behavior remains visible in the historical recording; this repair does not alter its numerical algorithm or claim full paper-benchmark reproduction.

## Historical release checks — 2026-09-17

This historical record includes checks of the combined interactive edition before the repositories were split. It is not the current acceptance result. Dash tests and recorded data live here; manuscript and article-build checks belong to the companion [paretoflow-myst repository](https://github.com/mikuknightforever/paretoflow-myst).

- All 60 Dash tests pass in the release checkout. Coverage includes stage playback, decision-by-decision disclosure, disabled controls before proposals exist, candidate inspection, full-record URL restoration, trace fidelity and the existing source/sample checks.
- The process UI tests exercise 71 HTTP callbacks; the largest tested response is 33,480 bytes. No training or new sampling is performed by the viewer.
- The combined edition once had 11 regression tests for a citation-theme patch. That patch and those tests were later removed when the article returned to the unmodified standard MyST theme; they are not current repository checks.
- All four article pages were built with the Bun-based release launcher. The older attribution of a download-path failure specifically to Node was not established and is withdrawn; the supported launcher and unmodified theme are documented in the article repository.
- Combined edition: the companion article preserves the original manuscript and appendix. Four mechanism views are embedded in the main paper and four supporting views in the supplement. Browser checks verified progressive stage changes, linked inspection, full-record context and compact reference typography. The historical checks below describe earlier versions; this is not a claim of a comprehensive device audit or a full benchmark reproduction.

## Independent repository split — 2026-09-17

The former `dash/` directory is now the root of `paretoflow-dash`, with its component history retained. The article is maintained independently in [paretoflow-myst](https://github.com/mikuknightforever/paretoflow-myst). The split changes repository organization and documentation; it makes no changes to runtime code, tests, recorded data or sampling algorithms. The local Dash address remains `http://localhost:8053`, so the existing article embeds continue to use the same routes. Each repository has its own startup instructions and dependency requirements.

All 60 tests passed again from this independent repository root. The process UI checks exercised 71 HTTP callbacks. Runtime code and data were also compared against the combined release at `cbcb17f`.

# Sample validation — 2026-09-09

- Recomputed analytic ZDT2 labels match all 60,000 bundled source records.
- Three sampling configurations completed with 161 recorded archive states each, 400 reference directions, and 30 design variables.
- Six unittest groups passed: HTTP routes, objective/dominance/hypervolume calculations, source/output hashes, bounds and stored objective values, selection/playback callback HTTP contracts, and linked design views/export.
- Initial evaluated hypervolume: 6.58357. Final values: guided 6.72256; no gradient guidance 6.70528; no neighbor exchange 6.64316. Fixed reference (1.1,10), original objective units, one seed only.
- Initial validation used HTTP/callback checks only. The recorded sample does not establish benchmark-level performance or author endorsement.

## Evolution playback fix — 2026-09-09

- All 12 unittest groups pass, including Node execution of the production playback reducer and frame mapper. Every one of the 161 browser frames matches the stored analytic coordinates.
- Regression checks cover pause versus a concurrent interval, ignored ticks while paused, resuming from the same frame, restarting from the early unchanged prefix, and stopping at frame 160.
- Verified in the article's actual iframe: pause held at frame 132 (t=0.825) across subsequent checks; Resume advanced to frame 136 (t=0.850), with 100 SVG point positions changing. Playback reached frame 160 and returned to Replay updates automatically.
- Scrubbing to frame 0 still displayed the original unchanged archive. Replay then began at frame 124 (t=0.775), and an immediate pause held there.
- Inspected the repaired panel visually in the current article viewport. This was a focused playback check, not a comprehensive responsive audit of the whole article.
- Evolution playback now runs locally without per-frame HTTP callbacks, repeated archive decompression, or rebuilding the complete analyzer's other plots. No experimental results or article theme files changed.

## Full-paper edition — 2026-09-09

- Read the pinned CC BY 4.0 arXiv v2 paper and appendix, and visually checked the original evaluation/table pages. Extracted all 23 HTML tables with source attribution and SHA-256, without digitizing figures.
- 18 test groups pass, including all 52 tasks × 22 methods × 2 percentiles (2,288 cells), missing-value handling, source numeric anchors, CSV round trips, numeric mean sorting, geometric filtering, neighboring selection, cost totals and the existing local playback/data checks.
- MyST builds both paper.md and appendix.md successfully. The live article contains all 11 intended embeds. It retains standard article-theme and a separate Dash service.
- Browser verification in the article: method stage changes; local-cone selection changes from an extreme point to the cone-constrained region; ZDT6 versus E2E shows the published -0.30 difference; the 50th-percentile view displays overall rank 4.85; selecting the diffusion ablation changes the task to C-10/MOP1; the table library opens Table 21 directly and exposes the correct values and CSV URL.
- Inspected the method and benchmark panels visually at the current desktop article width. This is not a comprehensive device matrix. The pre-existing MyST theme hydration warnings remain visible in the browser console; the page recovers and the tested controls work. No Dash callback failures were observed in the checked interactions.
- The original data, local checkpoints, original sampler and browser playback implementation were not changed by this full-paper expansion. The edition is an attributed adaptation, not a full benchmark reproduction.

## Complete explorer playback fix — 2026-09-16

- Replaced the complete explorer's Python playback-control callback with a synchronous browser callback sharing the evolution panel's state-transition logic. Figure generation remains on the server.
- Button events take priority over interval events in either batched order. Paused intervals leave playback state and the selected frame unchanged.
- Preserved the explorer's 350 ms interval, two-frame step, early-frame resume behavior and restart at frame 124 after reaching frame 160. The embedded evolution panel retains its one-frame step and early-prefix skip behavior.
- All 19 Python tests pass, including Node execution of both production JavaScript controllers, rapid pause/resume sequences, pause-versus-tick cases, end boundaries, all 161 recorded evolution frames, and a check that each explorer playback output has exactly one clientside writer.
- A loopback QA preview with a 900 ms delay on graph responses was prepared. Browser interaction was stopped by the browser safety check because it could not reliably determine the current URL; the slow-response browser acceptance check remains unverified.

## Recorded sampling process — 2026-09-16

- Added an optional synchronous observer to the sampler and a checkpoint-only trace producer. No training, random draws or in-place changes to sampling tensors occur in the observer. Detailed records cover directions 0, 100, 200, 300 and 399 for all 161 states in each of three configurations.
- For all three configurations, checkpoint replay exactly matches every original 400-direction archive, time, analytic objective, proxy prediction and final result. Trace enabled/disabled comparisons also match final proxy outputs and both Torch and NumPy RNG states exactly. Original sample and checkpoint SHA-256 hashes are unchanged.
- The 11,708,485-byte trace is loaded once on the server. It is not sent in full to the browser. Tested callbacks return at most 32,327 bytes and do not import Torch or run models.
- All 33 tests pass, including 7 independent trace-data tests and 7 process-view tests. These cover source hashes, state continuity, candidate identity, standardized-score geometry, actual admission masks, winners, clean-design archive updates, initial/transport states, 300 representative render combinations and 54 HTTP callbacks.
- In the actual in-app browser, verified step 160 to 159, slider return to the initial record, stage selection, table-candidate selection with linked design/state charts, and direction 100's explicit numerical-safeguard explanation. No browser error logs were observed during these checks. The process panel was inspected at normal and narrow viewport sizes; this is not a comprehensive device audit.
- Numerical limitation found in the original sampler: an unclamped acos can receive a cosine slightly above 1. Direction 100 has an undefined angular threshold, and the traced candidates include 3 undefined angles in guided, 5 in no-guidance and none in no-neighbors. The trace stores these as null and retains the actual original masks and argmin safeguard choices. It never describes them as zero angles or normal valid-angle decisions. Correcting the sampler's angle calculation would change the reference run and is separate from adding faithful replay.
