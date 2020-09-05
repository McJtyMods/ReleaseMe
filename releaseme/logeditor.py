import tkinter

class LogEditor(object):

    def add_log_entry(self):
        entry = self.log.get("1.0", tkinter.END).strip()
        self.add_to_log(entry)

    def edit_log_entry(self):
        selection = self.logentries.curselection()
        if selection:
            entry = self.logentries.get(selection)
            self.log.delete('1.0', tkinter.END)
            self.log.insert(tkinter.END, entry)

    def do_log(self):
        self.logentries.delete(0, tkinter.END)
        version = self.ui.get_selected_version()
        stdout, stderr = self.cmd.do_command("git", "log", "origin/" + version, "--oneline")
        self.logentries.delete(0, tkinter.END)
        for entry in stdout.splitlines():
            self.logentries.insert(tkinter.END, entry[8:])


    def __init__(self, ui, cmd, add_to_log):
        self.ui = ui
        self.cmd = cmd
        self.add_to_log = add_to_log

        self.top_frame = tkinter.Frame(ui.top_frame)
        self.top_frame.pack(fill="x")

        self.logentries = tkinter.Listbox(self.top_frame, exportselection=False)
        self.logentries.pack(side="top", anchor="n", fill="both")
        self.logentries.bind('<<ListboxSelect>>', lambda _ : self.edit_log_entry())

        frame = tkinter.Frame(self.top_frame)
        frame.pack(side = "bottom", fill="x")
        self.log = tkinter.Text(frame, height = 1)
        self.log.pack(side = "left", fill="x")
        self.add_button = tkinter.Button(frame, text = 'Add', command = self.add_log_entry)
        self.add_button.pack(side = "left")
