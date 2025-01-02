# VimDCC

Vim-like experience for PySide2 applications like Nuke, Maya, Houdini.

- [VimDCC](#vimdcc)
  - [Working DCCs](#working-dccs)
  - [Description](#description)
  - [Features](#features)
  - [Installation](#installation)
  - [Settings](#settings)
  - [Known Issues](#known-issues)
  - [Keybindings](#keybindings)
  - [Contributing](#contributing)

> [!IMPORTANT]
> The plugin is still in development and although most of the features are working, there are many bugs and missing features.

## Working DCCs

- [x] Nuke
- [ ] Maya
- [ ] Houdini (may not be possible, see [#2](https://github.com/sisoe24/vimdcc/issues/2))

## Description

VimDCC adds Vim-style functionality to QPlainTextEditor in PySide2 applications like Nuke, Maya, and Houdini. It's not a full Vim replacement but provides enough key features to make it worth your time.

![VimDCC](images/vimdcc.gif)

## Features

- **Modes**: Supports Normal, Insert, Visual, and Visual Line.
- **Persistent Registers**:
  - `Named`: Save and recall snippets.
  - `Clipboard`: Clipboard manager.
- **Search**: Vim-like search with `/`.
- **Marks**: Save and jump to positions.

Note: Some Vim motions and commands (e.g., `e`, `a`, `o/O`) have limited functionality. See [Known Issues](#known-issues) for details.

## Installation

1. **Download**: Get the latest release [here](https://github.com/sisoe24/vimdcc/releases#latest).
2. **Nuke Setup**:
   - Copy the `vimdcc` folder to `~/.nuke`.
   - Add this to your `menu.py` file:
     ```python
     from vimdcc import vimdcc
     vimdcc.install_nuke()
     ```
   - Access the plugin via *Nuke → Windows → Custom → VimDCC*.

## Settings

- **Launch on startup**: Enable/disable auto-launch and status bar placement.
- **Previewer auto-insert**: Automatically insert selected register (True/False).
- **Clipboard size**: Limit the number of stored snippets.
- **Copy to clipboard**: Sync registers with the system clipboard.

## Known Issues

General:

- **Key Commands**:
  - Deleting with `x`, `X`, `s` doesn’t save deleted characters to the register.
  - Unrecognized key commands can pile up in the input buffer. Press `Esc` to reset.
- **Session Limitation**: Only one editor is supported per session.
- **Motion Support**:
  - `e` motion does not handle punctuation correctly.
  - `a` text object doesn’t work well with the `w` motion.

Visual Mode:

- **Line Mode**: May fail in some cases, especially when navigating upward.
- **Search Motions**: Combining Visual mode with search can cause unexpected behavior.

Command Limitations:

- `o` and `O` commands don’t respect previous indentation.

## Keybindings

- `Ctrl+r`: Execute code
- `Alt+r`: Redo
- `\`: Show clipboard panel
- `'`: Show named registers
- `` ` ``: Show marks

## Contributing

Check the TODO.md file for planned features or to suggest improvements. Contributions are welcome!
