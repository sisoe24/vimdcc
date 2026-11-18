# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

## [0.2.0] - 2026-11-18

### Added

- Support for PySide6, so VimDCC runs in Nuke 16 and newer. PySide2 still works for Nuke 15 and older.

### Changed

- The insert cursor now has the same width however you enter Insert mode.
- The status bar shows the current mode next to the pending keys, for example `DELETE d`.
- Pasting from the clipboard preview (`\`) now inserts after the cursor, like `p`.

### Fixed

- VimDCC no longer fails to load when its registers or settings file is corrupt, for example after Nuke crashed while saving it, or when the file comes from an older version.
- Backspace now removes the last pending key.
- Ctrl+R no longer stops every command from working until you press Esc.
- Ctrl+R runs the script once, even after you close and reopen the VimDCC panel.
- `p` with an empty clipboard no longer shows an error and types a "p".
- `P` pastes a copied line above the current line, and `p` on the last line pastes below it.
- Searches (`/`, `?`, `*`, `#`) no longer replace your last yank or the system clipboard.
- Changing the clipboard size in the preferences now applies at once, without a restart.
- Two Nuke sessions open at the same time no longer overwrite each other's registers and marks.
- The keypad Enter key now runs a `/` or `?` search.
- Text objects such as `ci(` and `di"` no longer raise an error at the end of the document.

### Miscellaneous

- Switched development tooling from Poetry to uv.
- Added GitHub Actions that test against PySide2 and PySide6, and publish a release zip when a version tag is pushed.

## [0.1.0] - 2021-10-10

- Initial release
