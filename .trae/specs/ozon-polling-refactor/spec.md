# Ozon Task Polling & Scraper Refactor Spec

## Why
Currently, the Ozon upload process is "fire and forget". Users get a Task ID but don't know if the upload succeeded without manually checking.
Additionally, `WebScraperAgent` has become monolithic, making it harder to maintain and extend.

## What Changes
- **Ozon Task Polling**:
    - Implement a polling mechanism in `OzonApiManager` to check task status until completion (imported/failed).
    - Update `upload_to_ozon.py` to automatically poll status after upload.
    - Update `check_task_status.py` to support a `--watch` flag for continuous monitoring.
- **Scraper Refactoring**:
    - Refactor `WebScraperAgent` into a "Single Responsibility" structure.
    - Split into logical components: `Navigator` (browser control), `Extractor` (parsing), `Downloader` (assets).

## Impact
- **Affected Specs**: `upload_to_ozon.py`, `check_task_status.py`, `src/utils/ozon_api.py`, `src/agents/web_scraper_agent.py`.
- **Breaking Changes**: None expected, internal refactoring should maintain API compatibility.

## ADDED Requirements
### Requirement: Task Polling
The system SHALL poll the Ozon API for task status until a terminal state (`imported` or `failed`) is reached or a timeout occurs.

#### Scenario: Successful Upload
- **WHEN** user runs `python upload_to_ozon.py`
- **THEN** script uploads JSON, gets Task ID, polls status, and reports "Success: Imported X items".

#### Scenario: Watch Mode
- **WHEN** user runs `python check_task_status.py <task_id> --watch`
- **THEN** script polls status every N seconds until completion.

## MODIFIED Requirements
### Requirement: Refactored Scraper
`WebScraperAgent` SHALL delegate specific tasks to helper classes (`Navigator`, `Extractor`) instead of handling everything in one file.
