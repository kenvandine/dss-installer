import gi
import time
import os
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Snapd', '2')
from gi.repository import Gtk, Adw, GLib, Snapd
from console import Console

DSS_INSTALLER_DIR = os.path.dirname(os.path.realpath(__file__))

class MyApp(Adw.Application):

    def __init__(self):
        super().__init__(application_id='com.canonical.DataScienceStack')
        Adw.init()
        self.client = Snapd.Client()
        self.snaps = {
                'k8s': {'classic': True, 'channel': '1.32-classic/stable', 'installed': False},
                'kubectl': {'classic': True, 'channel': 'latest/stable', 'installed': False},
                'data-science-stack': {'classic': False, 'channel': '1.1/stable', 'installed': False},
        }
        self.installed = False
        self.initialized = False

    def do_activate(self):
        window = Adw.ApplicationWindow(application=self)
        window.set_default_size(1024, 768)

        # Create Adw.ToolbarView and add Adw.HeaderBar as the top bar
        toolbar_view = Adw.ToolbarView()
        header_bar = Adw.HeaderBar()
        header_bar_title = Gtk.Label(label="Data Science Stack")
        header_bar.set_title_widget(header_bar_title)
        header_bar.set_show_end_title_buttons(True)
        toolbar_view.add_top_bar(header_bar)
        window.set_content(toolbar_view)

        banner = Gtk.Picture.new_for_filename(os.path.dirname(os.path.realpath(__file__)) + "/banner.png")
        banner.set_halign(Gtk.Align.FILL)
        banner.set_valign(Gtk.Align.FILL)
        banner.set_can_shrink(False) # Prevent banner from shrinking when console is displayed
        
        self.setup_dss_button = Gtk.Button(label="Setup Data Science Stack")
        self.setup_dss_button.set_visible(False)
        self.setup_dss_button.connect("clicked", self.on_setup_dss_clicked)

        self.initialize_dss_button = Gtk.Button(label="Initialize Data Science Stack")
        self.initialize_dss_button.set_visible(True)
        self.initialize_dss_button.connect("clicked", self.on_initialize_dss_clicked)
        
        self.spinner = Gtk.Spinner()
        self.spinner.set_visible(False)

        self.ready = Gtk.Label(label="Your Data Science Stack is ready for use")
        self.ready.set_visible(False)
        markdown_text = """<b>Bold Text</b>\n<i>Italic Text</i>\n<u>Underlined Text</u>\n<a href='https://ubuntu.com/'>Link</a>\n\nMultiline support with \nnewlines and different styles."""
        main_content = Gtk.Label(label=markdown_text)
        main_content.set_use_markup(True)
        main_content.set_halign(Gtk.Align.START)
        main_content.set_valign(Gtk.Align.START)
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_top(20)
        vbox.set_margin_bottom(20)
        vbox.set_margin_start(20)
        vbox.set_margin_end(20)
        
        vbox.append(banner)
        vbox.append(self.setup_dss_button)
        vbox.append(self.initialize_dss_button)
        vbox.append(self.spinner)
        vbox.append(self.ready)
        vbox.append(main_content)

        self.labels = {}
        for snap in self.snaps.keys():
            label = Gtk.Label(label=snap)
            label.set_halign(Gtk.Align.START)
            self.labels[snap] = label
            vbox.append(label)

        # Add DSS and k8s to list
        k8s_configured = Gtk.Label(label="k8s Configured")
        k8s_configured.set_halign(Gtk.Align.START)
        self.labels['configured'] = k8s_configured
        vbox.append(k8s_configured)
        dss_initialized = Gtk.Label(label="DSS Initialized")
        dss_initialized.set_halign(Gtk.Align.START)
        self.labels['initialized'] = dss_initialized
        vbox.append(dss_initialized)

        # Add vbox of content to Adw.ToolbarView
        toolbar_view.set_content(vbox)

        # Display a terminal icon used to display stdout in a console
        console_icon = Gtk.Image()
        console_icon.set_from_icon_name("terminal")
        console_icon.set_pixel_size(24)
        console_icon.set_halign(Gtk.Align.START)
        vbox.append(console_icon)

        # Create a GestureClick object to handle clicking the icon
        console_gesture = Gtk.GestureClick()
        console_icon.add_controller(console_gesture)
        console_gesture.connect("pressed", self.on_show_console)

        # Console widget for displaying stdout
        self.console = Console()
        self.console.set_visible(False)
        vbox.append(self.console)

        window.present()

        # Query snapd for expected snaps
        self.client.get_snaps_async(Snapd.GetAppsFlags.NONE, list(self.snaps.keys()), None, self.handle_snap_list)

    # Handle showing/hiding Console
    def on_show_console(self, gesture, n_press, x, y):
        self.console.set_visible(not self.console.get_visible())

    # Has k8s been configured
    def is_k8s_configured(self):
        kube_config_path = os.path.join(os.path.expanduser("~"), ".kube/config")
        print(f"k8s configured: {os.path.exists(kube_config_path)}")
        return os.path.exists(kube_config_path)

    # Has DSS been initialize
    def is_dss_initialized(self):
        dss_config_path = os.path.join(os.path.expanduser("~"), "snap/data-science-stack/current/.dss/config")
        print(f"DSS initialized: {os.path.exists(dss_config_path)}")
        return os.path.exists(dss_config_path)

    def on_setup_dss_clicked(self, button):
        print("Get Started button clicked!.")
        self.setup_dss_button.set_visible(False)
        self.start_spinner()
        # Install all snaps not already installed
        for name in self.snaps.keys():
            if not self.snaps[name]['installed']:
                self.snap_install(name, self.snaps[name]['channel'], self.snaps[name]['classic'])

    def on_initialize_dss_clicked(self, button):
        print("Initialize button clicked!.")
        if not self.initialized and self.installed:
            self.initialize_dss_button.set_visible(False)
            self.start_spinner()
            self.console.set_visible(True)
            setup_script = os.path.join(DSS_INSTALLER_DIR, 'setup.sh')
            self.console.run_subprocess([setup_script], self.on_initialize_dss_finished)

    def on_initialize_dss_finished(self, ret):
        print(f"on_initialize_dss_finished: {ret}")
        if ret:
            self.stop_spinner()
        self.update_snaps_ui()

    def start_spinner(self):
        self.spinner.start()
        self.spinner.set_visible(True)
        self.setup_dss_button.set_visible(False)
        self.initialize_dss_button.set_visible(False)

    def stop_spinner(self):
        self.spinner.set_visible(False)
        self.spinner.stop()
        self.setup_dss_button.set_visible(not self.installed)
        self.initialize_dss_button.set_visible(not self.initialized)

    def handle_snap_list(self, client, result):
        try:
            snaps = client.get_snaps_finish(result)
            for snap in snaps:
                print(f"Name: {snap.get_name()}, Version: {snap.get_version()}, Revision: {snap.get_revision()}, Tracking: {snap.get_channel()}")
                name = snap.get_name()
                self.snaps[name]['channel'] = snap.get_channel()
                self.snaps[name]['installed'] = True
        except GLib.Error as e:
            print(f"Error: {e.message}")

        self.update_snaps_ui()

    # Update necessary UI elements based on state of installed snaps
    def update_snaps_ui(self):
        print(f"update UI elements based on state")
        #check for missing snaps and update UI as needed
        for name in list(self.snaps.keys()):
            if not self.snaps[name]['installed']:
                self.labels[name].set_text(f"✗ {name} not installed")
            else:
                self.labels[name].set_text(f"✅ {name}: installed")
        if self.is_k8s_configured():
            self.labels['configured'].set_text(f"✅ k8s Configured: True")
        else:
            self.labels['configured'].set_text(f"✗ k8s Configured: False")
        if self.is_dss_initialized():
            self.labels['initialized'].set_text(f"✅ DSS Initialized: True")
            self.initialized = True
        else:
            self.labels['initialized'].set_text(f"✗ DSS Initialized: False")
            self.initialized = False

        self.installed = any(snap['installed'] for snap in self.snaps.values())
        self.ready.set_visible(self.installed and self.initialized)
        if self.installed:
            print(f"All expected snaps found")
            self.stop_spinner()
        else:
            print(f"Missing expected snaps")
        self.setup_dss_button.set_visible(not self.installed)
        self.initialize_dss_button.set_visible(not self.initialized)

    def snap_install(self, package_name, channel="latest/stable", classic=False):
        print(f"snap_install: {package_name} {channel}")
        def handle_snap_install(client, result, user_data):
            print(f"handle_snap_install: {package_name}")
            try:
                res = client.install2_finish(result)
                print(f"Successfully installed {package_name}")
                self.snaps[package_name]['installed'] = res
                self.client.get_snaps_async(Snapd.GetAppsFlags.NONE, [package_name], None, self.handle_snap_list)
            except GLib.Error as e:
                print(f"Error finishing installation of {package_name}: {e.message}")

            self.update_snaps_ui()

        if not classic:
            flags = Snapd.InstallFlags.NONE
        else:
            flags = Snapd.InstallFlags.CLASSIC

        self.client.install2_async(flags, package_name, channel, None, None, None, None, handle_snap_install, None)


app = MyApp()
app.run(None)
