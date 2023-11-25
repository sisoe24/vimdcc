# VimDCC

VimDCC is a Vim lite client for some of the DCC applications (Nuke, Maya, Houdini, etc.). The plugin is written in Python and uses the [PySide2](https://wiki.qt.io/Qt_for_Python) library to create the UI.

> IMPORTANT: The plugin is still in development and although most of the features are working, there are many bugs and missing features. Feel free to report any issues, feature requests or contribute to the project.

## Description

The plugin is a lightweight Vim editor mode designed for DCC applications. It is not intended to be a full Vim implementation, but rather a subset of the most useful features.

The plugin works by installing itself as an event filter on a QPlainTextEditor. As a result, it intercepts all keyboard events and processes them before they are sent back. The plugin can be enabled or disabled at any time, and it only becomes active when the script editor is in focus.

## Features

- Vim like keybindings
- Normal, Insert, Visual, Visual Line modes
- Registers/Clipboard
- Search
- Marks

If you are familiar with Vim, you will feel right at home with the plugin. The plugin supports most of the basic Vim features so I won't go into too much detail here. Instead I will focus on the features that are specific to the plugin or differ from the Vim implementation.

### Modes

The plugin supports the following modes: Normal, Insert, Visual, Visual Line.

### Registers

Registers are somewhat similar to the Vim implementation. The key difference is that the plugin only supports the `named` register and the clipboard register. All of the registers are persistent, so you can close the application and the registers will still be there when you open it again.

#### Named Registers

The named registers is like a list of saved text snippets. You can save the text into a specific register and then paste it later. The plugin named registers are basically any key on the keyboard including numbers and special characters. The only exception is the `space` key which is not allowed.

Named registers include also the `last_search` register which is used to store the last search string.

Examples:

`"a`: Set the 'a' register

Now any command that involes the register will be performed on the `a` register:
 * `paste`: Paste the content of the `a` register
 * `y`: Yank the selected text into the `a` register

> The shortcut `"` is used to show the list of named registers. The list is displayed in an interactive window. You can use the arrow keys to navigate the list and press `Enter` to select a register. By default, the previewer will automatically select a register when it finds a match. You can disable this behavior by setting the `vimdcc.auto_insert_preview` option to `False`.

#### Clipboard Register

The clipboard register is something like the `numbered` register in Vim. It is a list of the last copied text snippets. The difference is that is more like a snippet manager: you can decide how many snippets you want to keep in the clipboard register.

The clipboard register is a circular buffer with a fixed size. When you copy a text snippet, it is added to the clipboard register. If the clipboard register is full, the oldest snippet is removed from the register.

To

## Keybindings

Some of the keybinding are different from the Vim implementation. This is still a work in progress and I will probably change some of the keybindings in the future.

- `Alt+r` - Redo
- `'` - Show clipboard register
- `"` - Show named registers
## Installation

### Nuke

To install the plugin in Nuke, copy the `vimdcc` folder to the `~/.nuke` folder. Then add the following lines to the `init.py` file:

```python
from vimdcc import vimdcc
vimdcc.install_nuke()
```
> If you are a NukeTools user, you can use the command `Nuke: Install VimDCC` from the vscode command palette.

## Development

At the moment the plugin is only tested for Nuke. I will add support for other DCC applications in the future. If you want to test the plugin in other applications, you can do so by adding the following lines to the `init.py` file of the application:


## Known Issues

This is a list of the most important issues that I am aware of.

- The `e` motion does not respect the punctuation characters.
- The `a` text object is not working properly.
- The `VISUAL LINE` mode fails to select the last line if the cursor is at the end of the line.
- `o` and `O` commands do not indent the new line.

## TODO

Vim is a very complex editor and I think is overkill for most of the tasks that we do in DCC script editor. If you are interesed to see a list of what might be implemented in the future, check the [TODO.md](TODO.md) file.


## Known Issues
