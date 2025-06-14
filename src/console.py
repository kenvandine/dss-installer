import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Gtk, GLib, Gdk
import subprocess
import threading
import os
import datetime

class Console(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.text_buffer = Gtk.TextBuffer()
        self.text_view = Gtk.TextView(buffer=self.text_buffer)
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.set_min_content_width(400)
        self.scrolled_window.set_min_content_height(200)
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_child(self.text_view)
        self.append(self.scrolled_window)
        self.visible = True

        # Load CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data("""
            .terminal {
                background-color: #300a24;
                color: #cccccc;
                font-family: "Ubuntu Mono";
                font-size: 12pt;
            }
        """)
        display = Gdk.Display.get_default()
        Gtk.StyleContext.add_provider_for_display(display, css_provider, 600)
        self.text_view.add_css_class("terminal")

        # Create directory for logs and define timestamped logfile
        xdg_cache_dir = os.environ.get('XDG_CACHE_HOME', '~/.cache')
        xdg_cache_dir = os.path.expanduser(xdg_cache_dir)
        log_dir = os.path.join(xdg_cache_dir, 'dss-installer')
        os.makedirs(log_dir, exist_ok=True)
        log_file = f"{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
        self.log_file = os.path.join(log_dir, log_file)

        # Automatically scroll to the end
        self.scroll_to_end()

        # Connect the signal to scroll to the end when new text is added
        self.text_buffer.connect("changed", self.scroll_to_end)

    def run_subprocess(self, command, callback):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        threading.Thread(target=self.read_output, args=(process,callback,)).start()

    def read_output(self, process, callback):
        for line in process.stdout:
            GLib.idle_add(self.append_text, line)
        ret = process.wait()
        callback(ret == 0)

    def scroll_to_end(self, userdata=None):
        # Get the vertical adjustment of the ScrolledWindow
        adjustment = self.scrolled_window.get_vadjustment()
        # Set the value to the maximum value to scroll to the end
        adjustment.set_value(adjustment.get_upper() - adjustment.get_page_size())

    def append_text(self, text):
        # Update textbuffer for UI
        self.text_buffer.insert(self.text_buffer.get_end_iter(), text)
        # Also append to timestamped logfile
        with open(self.log_file, 'a') as f:
            print(text, file=f, end='')
