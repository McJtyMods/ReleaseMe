import tkinter


class Ui(object):

    SELECT_MOD = "select_mod"
    SELECT_VERSION = "select_version"
    UPDATE_VERSION = "update_version"
    BUILD = "build"
    ROLLBACK = "rollback"
    PUSH = "push"
    RELEASE = "release"
    NEW_LOG = "new_log"

    def __init__(self):
        self.root = tkinter.Tk()
        self.root.title("ReleaseMe!")

        self.orig_curversion = ''
        self.orig_curtype = ''
        self.orig_mcjtylibversion = ''
        self.orig_baseversion = ''

        self.actions = {}

        # You will first create a division with the help of Frame class and align them on TOP and BOTTOM with pack() method.
        self.top_frame = tkinter.Frame(self.root)
        self.top_frame.pack()

        self.main = tkinter.Frame(self.top_frame)
        self.main.pack(side="top")

        self.__setup_mods()

        self.versions = tkinter.Listbox(self.main, exportselection=False, width=10)
        self.versions.pack(side="left", anchor="n", fill="y")
        self.versions.bind("<<ListboxSelect>>", lambda _ : self.__perform_action(Ui.SELECT_VERSION))

        self.infopanel = tkinter.Frame(self.main, width=50)
        self.infopanel.pack(side="right")

        self.curversion = self.__add_labeled_text(self.infopanel, 'Version')
        self.curtype = self.__add_labeled_text(self.infopanel, 'Type')
        self.mcjtylibversion = self.__add_labeled_text(self.infopanel, 'McJtyLib')
        self.baseversion = self.__add_labeled_text(self.infopanel, 'RFToolsBase')

        self.__create_buttons(self.infopanel)

        self.changelog = tkinter.Text(self.infopanel)
        self.changelog.pack(side="bottom")
        self.changelog.tag_configure("HIGH", foreground="blue")

        self.console = tkinter.Text(self.main, width=50)
        self.console.pack(side="right", fill="y")
        self.console.tag_configure("CMD", foreground="blue", font="bold")
        self.console.tag_configure("ERR", foreground="red")

    def __setup_mods(self):
        self.mods = tkinter.Listbox(self.main, exportselection=False)
        self.mods.pack(side="left", anchor="n", fill="y")
        self.mods.bind('<<ListboxSelect>>', lambda _: self.__perform_action(Ui.SELECT_MOD))
        self.mods.insert(tkinter.END, "McJtyLib")
        self.mods.insert(tkinter.END, "RFToolsBase")
        self.mods.insert(tkinter.END, "RFToolsDimensions")
        self.mods.insert(tkinter.END, "RFToolsUtility")
        self.mods.insert(tkinter.END, "RFToolsPower")
        self.mods.insert(tkinter.END, "RFToolsBuilder")
        self.mods.insert(tkinter.END, "RFToolsStorage")
        self.mods.insert(tkinter.END, "RFToolsControl")
        self.mods.insert(tkinter.END, "Restrictions")
        self.mods.insert(tkinter.END, "XNet")
        self.mods.insert(tkinter.END, "TheOneProbe")
        self.mods.insert(tkinter.END, "DeepResonance")
        self.mods.insert(tkinter.END, "LostCities")
        self.mods.insert(tkinter.END, "InControl")
        self.mods.insert(tkinter.END, "FxControl")
        self.mods.insert(tkinter.END, "McJtyLib")
        self.mods.insert(tkinter.END, "XNet")
        self.mods.insert(tkinter.END, "BurnNGrind")

    def __add_labeled_text(self, parent, text):
        panel = tkinter.Frame(parent)
        panel.pack(side="top")
        tkinter.Label(panel, text = text, width=10).pack(side = "left")
        widget = tkinter.Text(panel, height=1)
        widget.pack()
        return widget

    def __perform_action(self, action):
        self.actions[action]()

    def register_action(self, action, func):
        self.actions[action] = func

    def start(self):
        self.root.mainloop()

    def clear_changelog(self):
        self.changelog.delete('1.0', tkinter.END)
        self.curversion.delete('1.0', tkinter.END)
        self.curtype.delete('1.0', tkinter.END)
        self.mcjtylibversion.delete('1.0', tkinter.END)
        self.baseversion.delete('1.0', tkinter.END)

    def insert_versions(self, branches):
        self.versions.delete(0, tkinter.END)
        for branch in branches:
            self.versions.insert(0, branch)

    def get_selected_mod(self):
        curmod = self.mods.curselection()
        if curmod:
            return self.mods.get(curmod)
        else:
            return None

    def get_selected_version(self):
        curmod = self.mods.curselection()
        curversion = self.versions.curselection()
        if curmod and curversion:
            return self.versions.get(curversion)
        else:
            return None

    def reset_version_type(self):
        type = self.get_type()
        self.orig_curtype = type
        version = self.get_version()
        self.orig_curversion = version
        mcjtylibversion = self.get_mcjtylibversion()
        self.orig_mcjtylibversion = mcjtylibversion
        baseversion = self.get_baseversion()
        self.orig_baseversion = baseversion
        return version, type, mcjtylibversion, baseversion

    def set_version_type(self, version, type, mcjtylibversion, baseversion):
        self.curversion.delete('1.0', tkinter.END)
        self.curversion.insert(tkinter.END, version)
        self.orig_curversion = version

        self.curtype.delete('1.0', tkinter.END)
        self.curtype.insert(tkinter.END, type)
        self.orig_curtype = type

        self.mcjtylibversion.delete('1.0', tkinter.END)
        self.mcjtylibversion.insert(tkinter.END, mcjtylibversion)
        self.orig_mcjtylibversion = mcjtylibversion

        self.baseversion.delete('1.0', tkinter.END)
        self.baseversion.insert(tkinter.END, baseversion)
        self.orig_baseversion = baseversion

    def check_dirty(self, modified, branch, select_version):
        type = self.get_type()
        version = self.get_version()
        mcjtylibversion = self.get_mcjtylibversion()
        baseversion = self.get_baseversion()
        dirty = self.orig_curtype.strip() != type or self.orig_curversion.strip() != version or self.orig_mcjtylibversion.strip() != mcjtylibversion or self.orig_baseversion.strip() != baseversion
        self.update_button["state"] = "normal" if dirty else "disabled"
        self.push_button["state"] = "normal" if modified else "disabled"
        self.rollback_button["state"] = "normal" if modified else "disabled"

        selected_version = self.versions.curselection()
        version_list = self.versions.get(0, tkinter.END)
        if branch in version_list:
            idx = version_list.index(branch)
            if (not selected_version) or selected_version[0] != idx:
                self.versions.selection_clear(0, tkinter.END)
                self.versions.selection_set(idx)
                select_version()

        return dirty

    def get_type(self):
        return self.curtype.get("1.0", tkinter.END).strip()

    def get_version(self):
        return self.curversion.get("1.0", tkinter.END).strip()

    def get_mcjtylibversion(self):
        return self.mcjtylibversion.get("1.0", tkinter.END).strip()

    def get_baseversion(self):
        return self.baseversion.get("1.0", tkinter.END).strip()

    def log_console(self, line, tag):
        self.console.insert(tkinter.END, line, tag)
        self.console.see(tkinter.END)

    def __create_buttons(self, parent):
        self.buttonpanel = tkinter.Frame(parent)
        self.buttonpanel.pack()

        self.update_button = tkinter.Button(self.buttonpanel, text="Update")
        self.update_button.pack(side="left")
        self.update_button.bind("<Button-1>", lambda _ : self.__perform_action(Ui.UPDATE_VERSION))
        self.new_logentry = tkinter.Button(self.buttonpanel, text="New Log")
        self.new_logentry.pack(side="left")
        self.new_logentry.bind("<Button-1>", lambda _ : self.__perform_action(Ui.NEW_LOG))
        self.build_button = tkinter.Button(self.buttonpanel, text="Build")
        self.build_button.pack(side="left")
        self.build_button.bind("<Button-1>", lambda _ : self.__perform_action(Ui.BUILD))
        self.rollback_button = tkinter.Button(self.buttonpanel, text="Rollback")
        self.rollback_button.pack(side="left")
        self.rollback_button.bind("<Button-1>", lambda _ : self.__perform_action(Ui.ROLLBACK))
        self.push_button = tkinter.Button(self.buttonpanel, text="Push")
        self.push_button.pack(side="left")
        self.push_button.bind("<Button-1>", lambda _ : self.__perform_action(Ui.PUSH))
        self.release_button = tkinter.Button(self.buttonpanel, text="Release")
        self.release_button.pack(side="left")
        self.release_button.bind("<Button-1>", lambda _ : self.__perform_action(Ui.RELEASE))

    def disable_input(self):
        self.update_button["state"] = "disabled"
        self.push_button["state"] = "disabled"
        self.rollback_button["state"] = "disabled"
        self.build_button["state"] = "disabled"
        self.release_button["state"] = "disabled"
        self.new_logentry["state"] = "disabled"
        self.mods["state"] = "disabled"
        self.versions["state"] = "disabled"
        self.curversion["state"] = "disabled"
        self.curtype["state"] = "disabled"

    def enable_input(self):
        self.update_button["state"] = "normal"
        self.push_button["state"] = "normal"
        self.rollback_button["state"] = "normal"
        self.build_button["state"] = "normal"
        self.release_button["state"] = "normal"
        self.new_logentry["state"] = "normal"
        self.mods["state"] = "normal"
        self.versions["state"] = "normal"
        self.curversion["state"] = "normal"
        self.curtype["state"] = "normal"

