import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Gdk', '4.0')
from gi.repository import Gtk, GLib, Gdk
import subprocess
import threading

class Console(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.text_buffer = Gtk.TextBuffer()
        self.text_view = Gtk.TextView(buffer=self.text_buffer)
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_min_content_width(400)
        scrolled_window.set_min_content_height(200)
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_child(self.text_view)
        self.append(scrolled_window)
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

    def run_subprocess(self, command):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        threading.Thread(target=self.read_output, args=(process,)).start()

    def read_output(self, process):
        for line in process.stdout:
            GLib.idle_add(self.append_text, line)
        process.wait()

    def append_text(self, text):
        self.text_buffer.insert(self.text_buffer.get_end_iter(), text)
