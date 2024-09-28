# tkinter-edit
A basic text editor made in Tkinter.

Features:
- Word count and character count, both including and excluding newlines.
- Run and evaluate Python statements on the text for fast editing.

## Usage
- A home file will be opened on start (`tkinter_edit_save.txt`).
- Save, create and open files using the toolbar menu.
- Files are not written to disk until they are saved using the toolbar menu or the hotkey `Ctrl+S`.

## Advanced Usage
- Run Python statements using the toolbar menu. Warning: This application permits arbitrary and unlimited execution of Python statements.

- Statements that evaluate to a string will replace the text content. `t` or `text` contains the current text.
For example, to replace all instances of 'cat' with 'dog' in the entire text, run:

```py
t.replace('cat', 'dog')
```

- Any other result will be outputted to the console standard output.

- The modules attribute has been hard-coded and allows functions from other modules to be run from the Run menu. See the docstring for App.run_module for further details.

- The character count starts from the position set in the toolbar menu and automatically terminates at the symbol `---`.
