# VimDCC

- [VimDCC](#vimdcc)
  - [Description](#description)
  - [Features](#features)
  - [Differences from Vim](#differences-from-vim)
  - [Installation](#installation)
    - [Nuke](#nuke)
  - [Settings](#settings)
  - [Known Issues and Limitations](#known-issues-and-limitations)
  - [Keybindings](#keybindings)
  - [TODO](#todo)
  - [Contributing](#contributing)


> IMPORTANT: The plugin is still in development and although most of the features are working, there are many bugs and missing features. Feel free to report any issues, feature requests or contribute to the project.

## Description

VimDCC is a lightweight Vim editor plugin designed for PySide2 that offers a subset of the most useful features. Although it's not a complete Vim implementation, it can be used as a drop-in replacement for the default text editor console in Nuke and any other PySide2 application. In the future, I plan to add support for other applications like Maya and Houdini.

The plugin operates by installing itself as an event filter on a QPlainTextEditor. This enables it to intercept all keyboard events and process them before they're sent back. The plugin can be enabled or disabled at any time and it only activates when the QPlainTextEditor widget is in focus.

## Features

- Vim like keybindings
- Normal, Insert, Visual, Visual Line modes
- Registers/Clipboard
- Search
- Marks

If you know Vim, you'll feel at home with the plugin. It has most of Vim's basic features, so I won't go into detail. Instead, I'll focus on unique or different features.

## Differences from Vim

**Modes**

The plugin only supports the following modes: Normal, Insert, Visual, Visual Line.

**Registers**

This plugin has two registers (`named` and `clipboard`) that are similar to Vim's implementation. All registers are persistent.

* `named`

  Named registers are like saved text snippets that can be easily pasted later. Named registers include any key on the keyboard except for the `space` key. The `last_search` register is stored in the `/` register.

  Examples:

  * Copy the current line to the `a` register: `"ayy`
  * To paste from the last search register : `"/p`

  > Use `"` to see the list of named registers. Navigate it with arrow keys and select a register with `Enter`. The previewer automatically selects a register when it finds a match, but you can turn off this option in the setting panel by setting `Previewer auto insert` to `False`.

* `clipboard`

  The clipboard register in VimDCC stores a list of the last copied text snippets, acting as a snippet manager. It's a circular buffer with a fixed size, where you can decide how many snippets to keep. When it's full, the oldest snippet is removed. Like the `named` preview panel, you can press `'` to access the clipboard register, displayed in an interactive window, where you can navigate the list with arrow keys and select a snippet by pressing Enter.

## Installation

### Nuke

To install the plugin in Nuke, copy the `vimdcc` folder to the `~/.nuke` folder. Then add the following lines to the `menu.py` file:

```python
from vimdcc import vimdcc
vimdcc.install_nuke()
```
> If you are a NukeTools user, you can use the command `Nuke: Install VimDCC` from the vscode command palette.

## Settings

The settings are stored in the `.../vimdcc/vimdcc.json` file.

- `Launch on startup` - If `True`, the plugin will be enabled on startup. This settings also influences the Status Bar visibility. If `False`, the Status Bar will be attached to the bottom of the plugin window. If `True`, the Status Bar will be attached to the bottom of the Script Editor window.
- `Previewer auto insert` - If `True`, the previewer will automatically insert the selected register when it finds a match. If `False`, you have to press `Enter` to insert the selected register.
- `Clipboard size` - The number of snippets to keep in the clipboard register.
- `Copy to clipboard` - If `True`, the plugin will copy the selected register to the system clipboard.

## Known Issues and Limitations

This is a list of the most important issues that I am aware of and not a complete list of all the bugs or of all the missing features.

Nuke only:
  - To execute the code in the console while in Normal mode, you have to press `Ctrl+r` instead of `Enter`.

General:
- Deleting a character with `x`, `X`, `s` does not add the deleted character to the register.
- If you press a key that doesn't correspond to any command, it won't execute anything and will wait for the next key. This can result in a pile-up of invalid keys that will never be resolved. To clear the stack and start fresh, just press the `Esc` key.
- At the moment, the plugin only supports one editor per session. This means that only the first QPlainTextEditor widget will be enabled.
- The `e` motion does not respect the punctuation characters.
- The `a` text object not does work properly with the `w` motion.
- The `VISUAL LINE` mode does not work properly in some cases.
- `o` and `O` commands do not respect previous indentation.

## Keybindings

Some of the keybinding are different from the Vim implementation. This is still a work in progress and I will probably change some of the keybindings in the future.

- `Ctrl+r` - Run code in console (Normal mode)
- `Alt+r` - Redo
- `\` - Show clipboard panel (backslash)
- `'` - Show named panel (single quote)
- `` ` ``- Show marks panel (backtick)


## TODO

If you are interesed to see a list of what **might** be implemented in the future, check the [TODO.md](TODO.md) file. Feel free to add any feature requests or suggestions.

## Contributing

If you are interested in contributing to the project, please read the [CONTRIBUTING.md](CONTRIBUTING.md) file.
