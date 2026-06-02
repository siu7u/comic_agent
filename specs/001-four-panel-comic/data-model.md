# Data Model: Four-panel comic generation MVP

## ComicRequest

- **Fields**
- `theme`: string, required, non-empty
- `style`: string, optional
- `character`: string, optional
- `image_prompt`: string, optional global image guidance
- `panel_prompts`: map of panel index `1..4` to optional prompt text
- `reference_image_path`: string, optional, must point to a readable supported image file when present
- `lang`: string, default `zh`
- `output_dir`: string, required after CLI parsing/default resolution

- **Validation Rules**
- `theme` must be present before any pipeline stage starts
- `panel_prompts` may contain only panel indexes `1` through `4`
- `reference_image_path` must exist and match supported image file types when set

## CharacterBible

- **Fields**
- `summary`: canonical character description
- `appearance_traits`: list of recurring visual traits
- `personality_notes`: list of behavioral or emotional anchors when derivable
- `consistency_rules`: list of constraints that must appear in every final prompt

- **Relationships**
- Derived once from `ComicRequest`
- Referenced by all `PanelSpec` records

## StyleBible

- **Fields**
- `style_name`: normalized style label
- `tone`: atmosphere and mood notes
- `composition_rules`: framing or visual composition cues
- `rendering_traits`: recurring visual or artistic details

- **Relationships**
- Derived once from `ComicRequest`
- Referenced by all `PanelSpec` records

## StoryStructure

- **Fields**
- `title`: optional normalized story title
- `premise`: one-paragraph summary of the four-panel story
- `panels`: ordered list of exactly four `PanelSpec` items

- **Validation Rules**
- Must always contain exactly four panels
- Panel indexes must be unique and ordered `1..4`

## PanelSpec

- **Fields**
- `index`: integer `1..4`
- `caption`: string
- `dialogue`: string
- `scene_description`: string
- `action`: string
- `emotion`: string
- `camera_framing`: string
- `visual_description`: string
- `generated_prompt_base`: system-generated prompt before user guidance merge
- `final_image_prompt`: prompt after merge/rewrite
- `prompt_source`: enum `generated | merged | user_guided`
- `warnings`: list of rewrite or consistency warnings
- `retry_count`: integer `0..2`
- `image_path`: filesystem path to the panel PNG
- `input_mode`: enum `text_only | reference_guided`

- **Validation Rules**
- Every panel must include all textual fields required by the spec
- `prompt_source` must align with whether panel-specific or global guidance was applied
- `retry_count` must not exceed `2`

## MetadataRecord

- **Fields**
- `request`: normalized `ComicRequest`
- `character_bible`: `CharacterBible`
- `style_bible`: `StyleBible`
- `story`: `StoryStructure`
- `provider`: string, `MockImageProvider` for MVP
- `reference_image_path`: optional string
- `panel_image_paths`: ordered list of four paths
- `final_comic_path`: path to the 1054x1054 PNG
- `warnings`: request-level warnings
- `created_at`: timestamp string

- **Relationships**
- Aggregates the full result of one pipeline run
- Exported as `metadata.json` under the output directory

## ComicArtifactSet

- **Fields**
- `panel_images`: four 512x512 PNG files
- `final_comic`: one 1054x1054 PNG file
- `metadata`: one `metadata.json` file

- **Lifecycle**
1. Request parsed and validated
2. Shared bibles generated
3. Story and panel specs generated
4. Final prompts merged and safety-checked
5. Mock images generated with retries as needed
6. Final 2x2 comic composed
7. Metadata and file paths exported

## DocumentationDeliverable

- **Fields**
- `path`: repository-root `README.md`
- `sections`: installation/setup, CLI usage, required and optional arguments,
  example commands, expected output files, module responsibilities, MVP provider
  boundary, reference-image handling, test execution
- `scope`: documentation-only, not a runtime feature

- **Validation Rules**
- Must stay aligned with user-facing CLI behavior and output contracts
- Must be updated whenever setup steps, provider behavior, output files,
  metadata format, or test commands change
