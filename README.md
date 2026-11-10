# BRD analysis engine

P0 evaluation setup for a new DOCX BRD analysis engine.

- src: evaluation and corpus tooling
- tests: synthetic harness checks
- configs: evaluation guardrails
- docs: evaluation specifications
- fixtures: synthetic inputs; private inputs are ignored
- runs: private run artifacts
- reports: shareable measurements

Run the structure-only census with `python src/census.py ARCHIVE OUTPUT`.
The census reports OOXML marker counts, not interpreted layout fidelity.

Azure synthetic capability probes run with `python src/azure_probe.py` and write usage and timing to reports/azure-capabilities.json. They use only the configured Azure origin, cap concurrent calls at two by default and make one attempt per probe.

## P0 closeout commands

Run the closeout Azure probes with `python src/azure_probe.py --closeout`.
This sends three development document bodies to the configured Azure deployment for usage calibration. The archive must match the recorded development member hashes.
Run the credential scan with `python src/scan_secrets.py`. The scan excludes the credential file and reports counts.

The held-out gate command is `python src/heldout_gate.py SEALED_DIRECTORY TRUSTED_EVALUATOR`.
It checks the frozen hashes, invokes the evaluator once per run and suppresses subprocess logs.
The evaluator takes the sealed directory and run number and returns one JSON object on stdout
with numeric fields from the gate threshold config. Detailed failures, if needed, belong outside
the workspace and are for the user. An extraction evaluator is required for a real gate.
