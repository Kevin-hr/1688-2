# Tasks

- [ ] Task 1: Restore Source Code Access
  - [ ] SubTask 1.1: Verify existence of `src` folder. If missing, investigate and restore from backup or previous state.
  - [ ] SubTask 1.2: Ensure `python main.py --help` runs without import errors.

- [ ] Task 2: Implement Ozon Task Polling
  - [ ] SubTask 2.1: Add `poll_task_status(task_id, timeout=300, interval=5)` method to `OzonApiManager` in `src/utils/ozon_api.py`.
  - [ ] SubTask 2.2: Update `upload_to_ozon.py` to call `poll_task_status` after upload.
  - [ ] SubTask 2.3: Update `check_task_status.py` to support `--watch` argument using `poll_task_status`.

- [ ] Task 3: Refactor WebScraperAgent
  - [ ] SubTask 3.1: Create `src/agents/components/` directory (or similar structure).
  - [ ] SubTask 3.2: Extract `Navigator` class (browser setup, page navigation) from `WebScraperAgent`.
  - [ ] SubTask 3.3: Extract `Extractor` class (HTML parsing, data extraction) from `WebScraperAgent`.
  - [ ] SubTask 3.4: Extract `Downloader` class (image downloading) from `WebScraperAgent` (if not already handled by `FileManager`).
  - [ ] SubTask 3.5: Reassemble `WebScraperAgent` to use these components.
  - [ ] SubTask 3.6: Verify refactor with `python test_all_modules.py`.

# Task Dependencies
- Task 2 and Task 3 depend on Task 1 (Source Code Access).
- Task 3 can be done in parallel with Task 2 once Task 1 is complete.
