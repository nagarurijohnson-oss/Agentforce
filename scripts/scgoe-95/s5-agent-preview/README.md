# Session 5 conversation preview

- `drive.py` runs each scenario in `scenarios.json` as its own `sf agent preview` session against the local `Contact_Read_Agent` bundle with live actions, then reads the trace to record which actions ran, the template's raw output and the agent's raw reply. Output: `transcripts.json` (the final run is saved here as `transcripts-final.json`).
- `ui_preview.py` drives the Agentforce Builder Preview in Live Test Mode headlessly and saves screenshots. It never clicks Save, Commit Version or any publish control.
- Every utterance targets synthetic `CRA-TEST` records only. Paths in the scripts point at the Session 5 working folder; adjust before reuse.
