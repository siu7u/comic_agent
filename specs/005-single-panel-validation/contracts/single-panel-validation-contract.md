# Single-Panel Validation Contract

## Purpose

Define the contract for validating generated panel images, retrying failed
attempts, and preserving the existing comic pipeline contract.

## Generation Attempt Contract

- The system generates one image per provider attempt for one panel
- A provider-returned image is not automatically accepted
- Every attempt proceeds to a validation decision before panel acceptance

## Validation Contract

- Validation determines whether the image is usable as one full-frame
  single-scene illustration
- Validation may reject outputs that appear to contain internal subdivision,
  multiple frames, split-screen composition, montage, comparison layouts, or
  other multi-scene structures
- Validation must produce an explicit decision and reason for rejected or
  ambiguous attempts

## Retry Contract

- Rejected validation results trigger a bounded retry progression
- Each retry uses a named strategy profile
- Retry order is deterministic
- Retry exhaustion must end with an explicit panel failure state rather than an
  infinite loop

## Metadata Contract

Run metadata must record:

- panel attempt order
- strategy used for each attempt
- validation outcome for each attempt
- accepted attempt number when successful
- final panel failure reason when no attempt is accepted

## Compatibility Contract

- Story planning remains upstream and unchanged in contract shape
- Prompt generation remains upstream of provider execution
- Provider behavior remains image-generation-only
- Final composition still targets the existing `1054x1054` comic output with
  the existing `10px` `田`-shaped grid border

## Verification Contract

Automated verification must include:

- accepted validation path coverage
- rejected validation path coverage
- retry progression coverage
- retry exhaustion coverage
- metadata traceability coverage
- mock-safe pipeline compatibility coverage

Automated verification must not require:

- live provider access
- network access
- external agent frameworks
