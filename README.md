# VimDCC

- [VimDCC](#vimdcc)
  - [Description](#description)
  - [Features](#features)
  - [Differences from Vim](#differences-from-vim)
    - [Modes](#modes)
    - [Registers](#registers)
      - [Clipboard Register](#clipboard-register)
  - [Keybindings](#keybindings)
  - [Installation](#installation)
    - [Nuke](#nuke)
  - [Known Issues](#known-issues)
  - [TODO](#todo)
  - [Contributing](#contributing)


> IMPORTANT: The plugin is still in development and although most of the features are working, there are many bugs and missing features. Feel free to report any issues, feature requests or contribute to the project.

## Description

VimDCC is a PySide2 plugin that emulates a lightweight Vim editor specifically designed for DCC applications. While it does not aim to be a complete Vim implementation, it offers a subset of the most useful features.

The plugin works by installing itself as an event filter on a QPlainTextEditor. This allows it to intercept all keyboard events and process them before they are sent back. The plugin can be enabled or disabled at any time and only becomes active when the script editor is in focus.

## Features

- Vim like keybindings
- Normal, Insert, Visual, Visual Line modes
- Registers/Clipboard
- Search
- Marks

If you know Vim, you'll feel at home with the plugin. It has most of Vim's basic features, so I won't go into detail. Instead, I'll focus on unique or different features.

## Differences from Vim

### Modes

The plugin supports the following modes: Normal, Insert, Visual, Visual Line.

### Registers

This plugin has two registers (`named` and `clipboard`) that are similar to Vim's implementation. All registers are persistent.

* `named`

  Named registers are like saved text snippets that can be easily pasted later. Named registers include any key on the keyboard except for the `space` key. The `last_search` register is stored in the `/` register.

  Examples:

  * Copy the current line to the `a` register: `"ayy`
  * To paste from the last search register : `"/p`

  > Use `"` to see the list of named registers. Navigate it with arrow keys and select a register with `Enter`. The previewer automatically selects a register when it finds a match, but you can turn off this option in the setting panel by setting `Previewer auto insert` to `False`.

#### Clipboard Register

The clipboard register in VimDCC stores a list of the last copied text snippets, acting as a snippet manager. It's a circular buffer with a fixed size, where you can decide how many snippets to keep. When it's full, the oldest snippet is removed. Like the `named` preview panel, you can press `'` to access the clipboard register, displayed in an interactive window, where you can navigate the list with arrow keys and select a snippet by pressing Enter.

## Keybindings

Some of the keybinding are different from the Vim implementation. This is still a work in progress and I will probably change some of the keybindings in the future.

- `Alt+r` - Redo
- `'` - Show clipboard panel
- `"` - Show named panel
- `\``- Show marks panel

## Installation

### Nuke

To install the plugin in Nuke, copy the `vimdcc` folder to the `~/.nuke` folder. Then add the following lines to the `menu.py` file:

```python
from vimdcc import vimdcc
vimdcc.install_nuke()
```
> If you are a NukeTools user, you can use the command `Nuke: Install VimDCC` from the vscode command palette.

## Known Issues

This is a list of the most important issues that I am aware of.

- The `e` motion does not respect the punctuation characters.
- The `VISUAL LINE` mode fails to select the last line if the cursor is at the end of the line.
- `o` and `O` commands do not indent the new line.

## TODO

If you are interesed to see a list of what **might** be implemented in the future, check the [TODO.md](TODO.md) file. Feel free to add any feature requests or suggestions.

## Contributing

If you are interested in contributing to the project, please read the [CONTRIBUTING.md](CONTRIBUTING.md) file.
