import os
import queue
import subprocess
import threading


class CommandHandler(object):

    def __init__(self, ui):
        self.running_process = None
        self.running_finisher = None
        self.running_stdout = []
        self.output_queue = queue.Queue()
        self.output_stdout_queue = queue.Queue()
        self.ui = ui

    def do_command_log(self, finisher, *command):
        if self.running_process:
            # command_queue.put(command)
            print("Error! Already running!")
            return

        os.environ['PYTHONUNBUFFERED'] = "1"
        cmd = " ".join(command[:2])
        self.ui.log_console("\n" + cmd + "\n", "CMD")

        process =  subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        self.running_process = process
        self.running_finisher = finisher
        self.running_stdout = []
        self.ui.disable_input()
        t = threading.Thread(target = self.process_command_internal, args = (process,))
        t.start()

    def process_command_internal(self, process):
        self.process_output(process)
        while process.poll() is None:
            self.process_output(process)
        self.process_output(process)
        self.output_stdout_queue.put(self.running_stdout)

    def process_output(self, process):
        repeat = True
        while repeat:
            repeat = False
            line = process.stdout.readline()
            if line != "":
                self.output_queue.put((line,""))
                self.running_stdout.append(line.rstrip())
                repeat = True
            line = process.stderr.readline()
            if line != "":
                self.output_queue.put((line, "ERR"))
                repeat = True

    def process_command(self):
        while self.output_queue.qsize() > 0:
            line,tag = self.output_queue.get()
            self.ui.log_console(line, tag)

        if self.output_stdout_queue.qsize() > 0:
            stdout = self.output_stdout_queue.get()
            self.running_process = None
            self.ui.enable_input()
            if self.running_finisher:
                self.running_finisher(stdout)

        self.ui.root.after(100, self.process_command)

    def do_command(self, *command):
        process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        return process.communicate()
