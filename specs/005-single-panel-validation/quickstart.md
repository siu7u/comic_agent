# Quickstart: Single-panel generation validation and retry

## Goal

Verify that invalid nested multi-panel or storyboard-like images are rejected
before composition and that bounded retries can recover a panel automatically.

## Prerequisites

- Python 3.11+
- Project dependencies installed
- Local test environment without any required provider credentials

## Install

```bash
python3 -m pip install -e .[dev]
```

## Validation Verification Cases

Use these scenarios during implementation verification:

- one clearly valid single-scene panel attempt
- one clearly invalid subdivided or storyboard-like panel attempt
- one panel that fails first and passes on a later retry
- one panel that exhausts retries and ends in failure

## Expected Outcomes

### Accepted First Attempt

Expect:

- one panel attempt
- validation result `accepted`
- no retry
- panel included in final composition path

### Rejected Then Recovered

Expect:

- first attempt rejected by validation
- one later attempt accepted through a stricter strategy
- metadata shows both attempts and the acceptance boundary

### Retry Exhaustion

Expect:

- all bounded attempts rejected or failed
- no invalid panel silently accepted
- metadata records final failure reason

## Compatibility Check

Confirm that the existing pipeline contract still works:

- story planning still produces four planned panels
- provider generation still happens one panel attempt at a time
- final composition still expects four accepted panel images
- metadata remains readable and traceable

## Suggested Verification Commands

```bash
pytest tests/unit/test_metadata_export.py
pytest tests/unit/test_prompt_builder.py
pytest tests/integration/test_mock_pipeline.py
python3 -m compileall src tests
```

## README Check

Confirm repository-root `README.md` documents:

- that panel images may be rejected after generation
- that retries are bounded and traceable
- how to inspect validation and retry outcomes in metadata
