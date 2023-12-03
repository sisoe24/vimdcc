## VimDCC TODO

### DCC

- [x] Nuke
- [ ] Maya
- [ ] Houdini

### Misc
- [ ] Clear only a specific register
- [ ] Quick print
- [ ] Quick comment
- [ ] Highlighting
- [ ] Last cursor position
- [ ] Fallthrough default keybindings (e.g. `Ctrl-C`, `Ctrl-A`, etc.)
- [ ] Case insensitive search
- [x] Status Bar
- [x] Register preview

### Motions Commands
- [ ] `W` - Move to next WORD
- [ ] `B` - Move to previous WORD
- [ ] `E` - Move to end of WORD
- [ ] `{n}` Numbered motions
- [x] `w` - Move to next word
- [x] `b` - Move to previous word
- [x] `e` - Move to end of word
- [x] `h` - Move cursor left
- [x] `l` - Move cursor right
- [x] `k` - Move cursor up
- [x] `j` - Move cursor down
- [x] `0` - Move to start of line
- [x] `$` - Move to end of line
- [x] `^` - Move to first non-blank character of line

### Document Navigation
- [ ] `H` - Move to top of screen
- [ ] `M` - Move to middle of screen
- [ ] `L` - Move to bottom of screen
- [ ] `zz` - Move forward one screen
- [x] `gg` - Move to top of document
- [x] `G` - Move to bottom of document

### Text Insertion
- [x] `i` - Insert mode at cursor
- [x] `I` - Insert mode at start of line
- [x] `a` - Append mode after cursor
- [x] `A` - Append mode at end of line
- [x] `o` - Open new line below and enter insert mode
- [x] `O` - Open new line above and enter insert mode

### Text Modification
- [ ] `R` - Enter replace mode
- [x] `C` - Delete from cursor to end of line and enter insert mode
- [x] `cc` - Change entire line
- [x] `cM` - Change {mode} (e.g. `cw` to change word)
- [x] `~` - Toggle case of character under cursor
- [x] `r` - Replace character under cursor
- [x] `J` - Join line below to current line
- [x] `x` - Delete character under cursor
- [x] `D` - Delete from cursor to end of line
- [x] `dd` - Delete entire line
- [x] `S` - delete line and enter insert mod
- [x] `s` - delete character under cursor and enter insert mode

### Formatting
- [ ] `>>` - Indent line
- [ ] `<<` - Unindent line

### Undo/Redo

> NOTE: Undo/Redo are just wrappers around the application's undo/redo functionality. It is not a true Vim implementation.

- [ ] `U` - Undo all changes on line
- [ ] `.` - Repeat last change
- [x] `u` - Undo last change
- [x] `Ctrl-R` - Redo (Currently is `Alt-R`)

### Clipboard Operations
- [x] `y` - Yank (copy) text
- [x] `p` - Paste text after cursor
- [x] `P` - Paste text before cursor

### Marking
- [x] `m{char}` - Set mark at cursor position
- [x] ``{char}` - Move cursor to mark

### Search
- [x] `/` - Search forward
- [x] `?` - Search backward (Currently works as for forward search)
- [x] `n` - Next search result
- [x] `N` - Previous search result
- [x] `*` - Search forward for word under cursor
- [x] `#` - Search backward for word under cursor
- [x] `f{char}` - Move cursor to next occurrence of {char} on current line
- [x] `F{char}` - Move cursor to previous occurrence of {char} on current line
- [x] `t{char}` - Move cursor to before next occurrence of {char} on current line
- [x] `T{char}` - Move cursor to after previous occurrence of {char} on current line
- [x] `;` - Repeat previous `f`, `F`, `t`, or `T` command
- [x] `,` - Repeat previous `f`, `F`, `t`, or `T` command in opposite direction
- [x] Hook to `c`, `y`, `d`, `v` operators

### Visual Mode
- [x] `v` - Visual mode
- [x] `V` - Visual line mode

### Command Mode
- [ ] `:` - Enter command mode
- [ ] `:{n}` - Go to line {n}
- [ ] `python` - Run python code
- [ ] Dcc internal commands

### Text Objects

- [ ] `aw` - A word
- [ ] `iW` - Inner WORD
- [ ] `aW` - A WORD
- [x] `v` - Visual mode text object
- [x] `y` - Yank mode text object
- [x] `iw` - Inner word
- [x] `i(` - Inner parentheses
- [x] `a(` - A parentheses
- [x] `i{` - Inner curly braces
- [x] `a{` - A curly braces
- [x] `i[` - Inner square brackets
- [x] `a[` - A square brackets
- [x] `i'` - Inner single quotes
- [x] `a'` - A single quotes
- [x] `i"` - Inner double quotes
- [x] `a"` - A double quotes
- [x] `i\`` - Inner backticks
- [x] `a\`` - A backticks
