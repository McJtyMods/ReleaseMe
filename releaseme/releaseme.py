import os
import sys
import tkinter

from releaseme.commandhandler import CommandHandler
from releaseme.logeditor import LogEditor
from releaseme.ui import Ui

def goto_mod():
    os.chdir(maindir)
    mod = ui.get_selected_mod()
    if mod:
        os.chdir(mod)

def select_mod():
    mod = ui.get_selected_mod()
    if mod:
        os.chdir(maindir)
        cmd.do_command_log(select_mod_1, 'git', 'clone', 'https://github.com/McJtyMods/' + mod)

def select_mod_1(_):
    goto_mod()
    cmd.do_command_log(select_mod_2, 'git', 'branch', '-r')

def select_mod_2(stdout):
    branches = []
    for line in stdout:
        idx = str.index(str(line), 'origin/')
        branch = line[idx+7:]
        if not str.startswith(branch, "HEAD"):
            branches.append(branch)
    ui.insert_versions(branches)
    ui.clear_changelog()

def select_version():
    version = ui.get_selected_version()
    if version:
        goto_mod()
        cmd.do_command_log(select_version_1, 'git', 'checkout', version)

def select_version_1(_):
    scan_changelog()
    scan_gradle_properties()
    cmd.do_command_log(select_version_2, 'git', 'pull')

def select_version_2(_):
    logeditor.do_log()

def refresh_dirty():
    goto_mod()

    stdout, stderr = cmd.do_command("git", "status")
    modified = []
    branch = None
    for line in stdout.splitlines():
        line = line.decode('utf-8')
        if str.startswith(line, "On branch "):
            branch = line[10:]
        if "modified:" in line:
            modified.append(line)

    ui.check_dirty(modified, branch, select_version)
    ui.root.after(300, refresh_dirty)

def push():
    goto_mod()
    file = open("../github_pass", "r", encoding='utf-8')
    ww = file.readline().rstrip()
    file.close()

    cmd.do_command_log(lambda _: push_1(ww), "git", "add", "changelog.txt", "gradle.properties")

def push_1(ww):
    cmd.do_command_log(lambda _: push_2(ww), "git", "commit", "-m'Update version to " + ui.get_version() + "'")

def push_2(ww):
    cmd.do_command_log(None, "git", "push", "https://" + ww + "@github.com/McJtyMods/" + ui.get_selected_mod() + ".git")

def rollback():
    goto_mod()
    cmd.do_command("git", "reset")
    cmd.do_command("git", "checkout", ".")
    select_version()

def get_gradle_command():
    if sys.platform == "win32":
        return "gradlew.bat"
    else:
        return "./gradlew"

def new_log_line(line, result):
    if result:
        if line.strip() == '':
            # We found the place to add the entry
            return ["- " + result + "\n", line], None
        else:
            return line, result
    return line, result

def add_to_log(entry):
    replace_in_file('changelog.txt', new_log_line, entry)
    select_version()

def new_log_entry(line, result):
    if result:
        version = ui.get_version()
        return [version + ":\n", "\n", line], False
    return line, result

def new_log():
    goto_mod()
    replace_in_file('changelog.txt', new_log_entry, True)
    select_version()

def build():
    goto_mod()
    cmd.do_command_log(None, get_gradle_command(), "build")

def release():
    goto_mod()
    # ./gradlew curseforge -Pcurseforge_key=`cat ../curseforge_key`
    file = open("../curseforge_key", "r", encoding='utf-8')
    key = file.readline().rstrip()
    file.close()
    cmd.do_command_log(None, get_gradle_command(), "curseforge", "-Pcurseforge_key=" + key)

def replace_in_file(filename, transformer, result):
    file = open(filename, "r", encoding='utf-8')
    lines = file.readlines()
    newlines = []
    for line in lines:
        newline, result = transformer(line, result)
        if isinstance(newline, list):
            newlines.extend(newline)
        else:
            newlines += newline
    file.close()

    file = open(filename, "w", encoding='utf-8')
    file.writelines(newlines)
    file.close()
    return result

def update_version_gradle(line, result):
    version, type, mcjtylibversion, baseversion = result
    if str.startswith(line, "version="):
        line = line[:8] + version + "\n"
    if str.startswith(line, "mcjtylib_version="):
        line = line[:17] + mcjtylibversion + "\n"
    if str.startswith(line, "rftoolsbase_version="):
        line = line[:20] + baseversion + "\n"
    if str.startswith(line, "curse_type="):
        line = line[:11] + type + "\n"
    return line, result

def update_version_changelog(line, result):
    if result:
        return result + ":\n", None
    else:
        return line, None

def update_version():
    global orig_curversion
    global orig_curtype
    goto_mod()
    version, type, mcjtylibversion, baseversion = ui.reset_version_type()
    replace_in_file("gradle.properties", update_version_gradle, (version, type, mcjtylibversion, baseversion))
    replace_in_file("changelog.txt", update_version_changelog, version)
    cmd.do_command("git", "add", "changelog", "gradle.properties")
    select_version()

def scan_gradle_properties():
    global orig_curversion
    global orig_curtype
    goto_mod()
    try:
        file = open("gradle.properties", "r", encoding='utf-8')
    except FileNotFoundError:
        ui.set_version_type("<unknown>", "<unknown>", "<unknown>", "<unknown>")
        return
    lines = file.readlines()
    version = "<unknown>"
    type = "<unknown>"
    mcjtylibversion = ""
    baseversion = ""
    for line in lines:
        if str.startswith(line, "version="):
            version = line[8:]
        if str.startswith(line, "mcjtylib_version="):
            mcjtylibversion = line[17:]
        if str.startswith(line, "rftoolsbase_version="):
            baseversion = line[20:]
        if str.startswith(line, "curse_type="):
            type = line[11:]
    ui.set_version_type(version, type, mcjtylibversion, baseversion)

def scan_changelog():
    ui.changelog.delete('1.0', tkinter.END)
    goto_mod()
    try:
        file = open("changelog.txt", "r", encoding='utf-8')
    except FileNotFoundError:
        return
    lines = file.readlines()
    tag = "HIGH"
    cnt = 4
    for line in lines:
        if line.strip() == '':
            cnt -= 1
            if cnt < 0:
                break
            if tag == "HIGH":
                tag = ""
        ui.changelog.insert(tkinter.END, line, tag)



def main():
    global ui, cmd, maindir, logeditor

    ui = Ui()
    ui.register_action(Ui.SELECT_VERSION, select_version)
    ui.register_action(Ui.SELECT_MOD, select_mod)
    ui.register_action(Ui.UPDATE_VERSION, update_version)
    ui.register_action(Ui.BUILD, build)
    ui.register_action(Ui.ROLLBACK, rollback)
    ui.register_action(Ui.PUSH, push)
    ui.register_action(Ui.RELEASE, release)
    ui.register_action(Ui.NEW_LOG, new_log)

    cmd = CommandHandler(ui)

    logeditor = LogEditor(ui, cmd, add_to_log)

    maindir = os.getcwd()

    ui.root.after(300, refresh_dirty)
    ui.root.after(100, cmd.process_command)
    ui.start()

