"""A basic text editor made in Tkinter with a character count.
Opens a home file on start.
This application is unsafe; you may run Python statements using the menu.

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted.
THE SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY (etc.) IN NO EVENT
SHALL THE AUTHOR BE LIABLE FOR ANY DAMAGES WHATSOEVER (etc.) ARISING
OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""
import tkinter as tk
from tkinter import N, S, W, E, filedialog, simpledialog
from tkinter import ttk
from tkinter import font
from pathlib import Path
import importlib

# The default save location, to open on start.
save_location = "tkinter_edit_save.txt"
text_filetypes = [("text files", ".txt"), ("all files", ".*")]
work_start = "1.0"
# Number of changes until confirmation is required to close the application.
changes_threshold = 40

TK_TEXT_INDEX_INSTRUCTION = """For example, 1.0 is the start of the text.
Accepts also {line}.start, {line}.end, start, end."""

class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master.title("Tkinter Text Edit - Home ({})".format(save_location))
        self.master.resizable(True, True)

        self.text_font = font.Font(family="Consolas", size=11)
        self.char_count_var = tk.StringVar()
        self.changes = - changes_threshold  # counts up when key released
        
        self.create_widgets()
        self.with_style()

        try:
            with open(save_location, "r") as f:
                self.entry.insert("1.0", f.read())
        except FileNotFoundError:
            print("(file not found: start blank file)")

    def create_widgets(self):
        # Toolbar menu
        self.menu = tk.Menu(self.master)
        self.menu.add_command(label="Save", command=self.save_with_message)
        self.menu.add_command(label="New", command=self.set_file)
        self.menu.add_command(label="Open", command=lambda: self.set_open(True))
        self.menu.add_command(label="Join", command=lambda: self.set_open(False))
        self.menu.add_command(label="Characters", command=self.set_counter)
        self.menu.add_command(label="Seek", command=self.set_position)
        # Run sub-menu to run arbitrary Python statements and hardcoded modules
        cascade = tk.Menu(self.menu, tearoff=0)
        modules = [("url_parameter", lambda: self.run_module("url_parameter", ""))]
        for label, command in modules:
            if importlib.util.find_spec(label) is not None:
                cascade.add_command(label=label, command=command)
        cascade.add_separator()
        cascade.add_command(label="Run Statement", command=self.run_python_statement)
        self.menu.add_cascade(label="Run...", menu=cascade)
        self.master.config(menu=self.menu)

        # Frames
        self.in_frame = ttk.Frame(self.master, padding="5 5 0 5")
        self.in_frame.grid(column=0, row=1, sticky=(N, S, W, E))
        
        self.status_frame = ttk.Frame(self.master, padding="5 3 0 0")
        self.status_frame.grid(column=0, row=0, sticky=(S, W))

        # Widgets
        self.scrollbar = ttk.Scrollbar(self.in_frame)
        self.scrollbar.grid(column=1, row=1, sticky=(N, S))
        
        self.entry = tk.Text(self.in_frame, font=self.text_font, undo=True,
                             wrap=tk.WORD, yscrollcommand=self.scrollbar.set)
        self.entry.grid(column=0, row=1, sticky=(N, S, W, E))
        
        self.scrollbar.config(command=self.entry.yview)
        
        self.char_count = ttk.Label(self.status_frame, style="Dim.TLabel",
                                    textvariable=self.char_count_var)
        self.char_count.grid(column=0, row=0, sticky=(W, E))

        # Allow text field to fill space.
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=1)
        self.in_frame.columnconfigure(0, weight=1)
        self.in_frame.rowconfigure(1, weight=1)
        
        # Bind certain edits to the entry to updating the character count.
        self.entry.bind('<KeyRelease>', self.update)
        self.entry.bind('<ButtonPress-1>', self.update_select)
        self.entry.bind('<<Selection>>', self.update_select)

        self.master.bind('<Control-s>', self.save)
        
    def with_style(self):
        style = ttk.Style()
        style.configure("Result.TLabel", background="#d9e0df")
        style.configure("Result.TFrame", background="#d9e0df")
        style.configure("Dim.TLabel", foreground="#555555")

    def save(self, event=None):
        text_data_to_save = self.entry.get('1.0', tk.END)[:-1]  # remove trailing \n
        with open(save_location, "w+") as f:
            f.write(text_data_to_save)
        characters = len(text_data_to_save)
        linebreaks = text_data_to_save.count("\n")

        self.char_count_var.set("Saved {} characters ({})".format(
            characters - linebreaks, characters))
        self.changes = - changes_threshold - 2  # subtract Ctrl and S presses

    def save_with_message(self):
        self.save()
        print("Saved to {}. Shortcut: Ctrl-S".format(save_location))
        self.changes = - changes_threshold
        
    def set_counter(self):
        global work_start
        print("Current work start position is {}".format(work_start))
        
        new_work_start = simpledialog.askstring("Character Count Start",
            "Begin the character count from {line}.{character}\n"
            + TK_TEXT_INDEX_INSTRUCTION, parent=self.master)

        text_index = tk_text_index(new_work_start)
        if text_index:    
            work_start = text_index
            print("Set new work start position to {}".format(work_start))

        self.entry.tag_delete("promptline")
        self.entry.tag_add("promptline", "1.0", work_start)
        self.entry.tag_configure("promptline", foreground="#555555")

    def set_open(self, clear=False):
        global save_location
        print("Current save location is {}".format(save_location))
        
        open_location = filedialog.askopenfilename(parent=self.master,
            initialdir=Path.cwd(), filetypes=text_filetypes, defaultextension="txt")

        if open_location:
            save_location = open_location  # update global variable
            print("Set new save location to {}".format(save_location))
            self.master.title(str(save_location))
            
            try:
                with open(save_location, "r") as f:
                    if len(self.entry.get(work_start, tk.END)) > 1:
                        self.entry.insert("1.0", "\n---\n")
                        new_text_data = f.read()
            except FileNotFoundError:
                print("(file not found: keeping old data)")
            else:
                if clear:
                    self.entry.delete("1.0", tk.END)
                self.entry.insert("1.0", new_text_data)

    def set_file(self):
        global save_location
        print("Current save location is {}".format(save_location))
        
        new_save_location = filedialog.asksaveasfilename(parent=self.master,
            initialdir=Path.cwd(), filetypes=text_filetypes, defaultextension="txt")

        if new_save_location and not Path(new_save_location).is_dir():
            save_location = new_save_location
            print("Set new save location to {}".format(save_location))
            self.master.title(str(save_location))

    def update_select(self, event=None):
        try:
            text_data = self.entry.get("sel.first", "sel.last")
            self.set_character_count(text_data, 1)
        except tk.TclError:
            text_data = self.entry.get(work_start, tk.END)
            text_data = text_data.split("---")[0]  # ignore after ---
            self.set_character_count(text_data)

    def update(self, event=None):    
        # Increment counter to warn the user when closing with changes made.
        self.changes += 1
        # Update character count on releasing Backspace, Enter, Space, Insert, Del
        if event.keycode in (0x08, 0x0d, 0x20, 0x2d, 0x2e):
            text_data = self.entry.get(work_start, tk.END)
            text_data = text_data.split("---")[0]  # ignore after ---
            self.set_character_count(text_data)

    def set_character_count(self, text_data, add_to_count=0): 
        characters = len(text_data) + add_to_count - 1  # account for trailing \n
        linebreaks = text_data.count("\n") + add_to_count - 1
        words = len(text_data.split())
        
        self.char_count_var.set("{} characters ({})  {} words".format(
            characters - linebreaks, characters, words))

    def set_position(self):
        new_seek_position = simpledialog.askstring("Seek to Position",
            "Seek to {line}.{character},\n" + TK_TEXT_INDEX_INSTRUCTION,
            parent=self.master)

        text_index = tk_text_index(new_seek_position)
        if text_index:
            self.entry.see(text_index)

    def run_python_statement(self):
        """Evaluates a Python statement.
        If the function returns a string, it replaces the entry text."""
        code = simpledialog.askstring("Run Statement",
            "Evaluates a Python statement. 'text' or 't' contains the entry text.",
            parent=self.master)

        if code:
            text_data = self.entry.get(work_start, tk.END)[:-1]
            print(">>> {}".format(code))

            _globals = {"text": text_data, "t": text_data, "shift_character": shift_character}
            _locals = {}
            text_data = eval(compile(code, "<string>", mode="eval"),
                             _globals, _locals)

            self.try_replace_text(text_data)
        else:
            print("Cancelled python execution")

    def run_module(self, function, mode="text"):
        """Imports and runs the given function name within an external module
        of the same name. The function must take a single argument,
        either the entry text in 'text' mode or else an input string.
        If the function returns a string, it replaces the entry text."""
        module = importlib.import_module(function)
        if mode == "text":
            text_data = self.entry.get(work_start, tk.END)[:-1]
        else:
            text_data = simpledialog.askstring("Module Input",
                module.__doc__, parent=self.master)

        if hasattr(module, function) and text_data:
            text_data = getattr(module, function)(text_data)
            self.try_replace_text(text_data)
        else:
            print("Module execution failed\n... {}".format(text_data))

    def try_replace_text(self, text_data):
        if type(text_data) == str:
            self.entry.delete("1.0", tk.END)
            self.entry.insert("1.0", text_data)
            print("Undo changes with Ctrl-Z-Z")
        else:
            print("Statement must evaluate to string to set text",
                  "... {}".format(text_data), sep="\n")

    def on_exit(self):
        message = "Close application? Changes ({}) not saved.".format(
            self.changes + changes_threshold)
        if self.changes < 0 or tk.messagebox.askyesno("Exit", message):
            self.master.destroy()

def tk_text_index(position):
    if position:
        if position.lower() == "end":
            return tk.END
        
        offsets = ["1", "0"]
        new_offsets = position.split(".")
        
        if len(new_offsets) > 0 and new_offsets[0].isdigit():
            offsets[0] = new_offsets[0]
        if len(new_offsets) > 1:
            if new_offsets[1].isdigit():
                offsets[1] = new_offsets[1]
            elif new_offsets[1].lower() == "end":
                offsets[1] = tk.END
        return ".".join(offsets)
    return None

# Helper function accessible in an eval function
def shift_character(char, n):
    if ord('a') <= ord(char) <= ord('z'):
        offset = ord('a')
    elif ord('A') <= ord(char) <= ord('Z'):
        offset = ord('A')
    else:
        return char
    return chr((ord(char) + n - offset) % 26 + offset)


# Start Tk.
if __name__ == "__main__":
    root = tk.Tk()
    app = App(master=root)

    # Intercept an exit event in case changes have been made
    root.protocol("WM_DELETE_WINDOW", app.on_exit)
    root.mainloop()
    quit()
