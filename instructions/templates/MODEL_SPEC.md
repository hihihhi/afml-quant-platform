# Model specification — draft contract template

Identity/source IDs; prediction target and label timing; feature availability;
training/validation/holdout split identity; sample-weight semantics; train-only
preprocessing; fitting randomness and reproducibility; hyperparameter search/trial
ledger; scoring/calibration conventions; serialized artifact/version/fit interval;
input/output schema; unknown/missing data behavior; numerical tolerance; reference
and native inference/training comparisons; training and inference performance
separately; independent evidence and approval. Do not select a library merely
because the book used an old Python API. Preserve the old semantics, then document
and test an implementation-compatible translation explicitly.
