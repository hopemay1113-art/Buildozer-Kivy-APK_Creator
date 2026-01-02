from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.core.window import Window
import json
import os

# Request Android permissions
try:
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.QUERY_ALL_PACKAGES,
        Permission.READ_EXTERNAL_STORAGE,
        Permission.WRITE_EXTERNAL_STORAGE,
    ])
except ImportError:
    pass

# Try to get installed packages
try:
    from jnius import autoclass
    PythonJavaClass = autoclass('org.renpy.android.PythonJavaClass')
    pm = PythonJavaClass.activity.getPackageManager()
    
    def get_installed_apps():
        """Get list of installed app packages."""
        try:
            packages = pm.getInstalledPackages(0)
            app_list = []
            for i in range(packages.size()):
                pkg = packages.get(i)
                app_name = pkg.packageName
                # Skip system apps
                if not app_name.startswith('android') and not app_name.startswith('com.android'):
                    app_list.append(app_name)
            return sorted(app_list)
        except:
            return []
except ImportError:
    def get_installed_apps():
        """Fallback: return demo apps."""
        return ['com.example.game1', 'com.example.game2', 'com.example.app1']


class AppSettingsManager:
    """Manages app settings using JSON storage."""
    
    def __init__(self):
        self.settings_file = os.path.join(os.path.expanduser('~'), 'app_settings.json')
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from file or return empty dict."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_settings(self):
        """Save settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get_app_settings(self, app_name):
        """Get settings for a specific app."""
        if app_name not in self.settings:
            self.settings[app_name] = {
                'fps_cap': 60,
                'target_fps': 60,
                'refresh_rate': 60
            }
            self.save_settings()
        return self.settings[app_name]
    
    def update_app_setting(self, app_name, key, value):
        """Update a setting for an app."""
        if app_name not in self.settings:
            self.settings[app_name] = {}
        self.settings[app_name][key] = value
        self.save_settings()


class VRSettingsApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings_manager = AppSettingsManager()
        self.current_app = None
    
    def build(self):
        Window.size = (400, 800)
        self.title = 'Cyn Enhancements'
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = Label(text='VR App Settings Manager', size_hint_y=0.1, font_size='20sp', bold=True)
        main_layout.add_widget(header)
        
        # Apps list (scrollable)
        scroll_view = ScrollView(size_hint=(1, 0.9))
        self.apps_grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.apps_grid.bind(minimum_height=self.apps_grid.setter('height'))
        
        # Populate with installed apps
        installed_apps = get_installed_apps()
        if not installed_apps:
            self.apps_grid.add_widget(Label(text='No apps found', size_hint_y=None, height=50))
        else:
            for app in installed_apps:
                btn = Button(
                    text=app,
                    size_hint_y=None,
                    height=50,
                    background_color=(0.2, 0.6, 0.8, 1)
                )
                btn.bind(on_press=self.show_app_settings)
                self.apps_grid.add_widget(btn)
        
        scroll_view.add_widget(self.apps_grid)
        main_layout.add_widget(scroll_view)
        
        return main_layout
    
    def show_app_settings(self, instance):
        """Show settings popup for selected app."""
        app_name = instance.text
        self.current_app = app_name
        settings = self.settings_manager.get_app_settings(app_name)
        
        # Create popup content
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title = Label(text=f'Settings: {app_name}', size_hint_y=0.15, font_size='18sp', bold=True)
        content.add_widget(title)
        
        # Settings scroll view
        scroll = ScrollView()
        settings_layout = GridLayout(cols=1, spacing=10, size_hint_y=None, padding=10)
        settings_layout.bind(minimum_height=settings_layout.setter('height'))
        
        # FPS Cap Slider
        fps_cap_label = Label(
            text=f'FPS Cap: {int(settings["fps_cap"])}',
            size_hint_y=None,
            height=30
        )
        settings_layout.add_widget(fps_cap_label)
        
        fps_cap_slider = Slider(
            min=30,
            max=240,
            value=settings['fps_cap'],
            size_hint_y=None,
            height=40
        )
        
        def update_fps_cap(slider):
            val = int(slider.value)
            fps_cap_label.text = f'FPS Cap: {val}'
            self.settings_manager.update_app_setting(app_name, 'fps_cap', val)
        
        fps_cap_slider.bind(value=update_fps_cap)
        settings_layout.add_widget(fps_cap_slider)
        
        # Target FPS Slider
        target_fps_label = Label(
            text=f'Target FPS: {int(settings["target_fps"])}',
            size_hint_y=None,
            height=30
        )
        settings_layout.add_widget(target_fps_label)
        
        target_fps_slider = Slider(
            min=30,
            max=240,
            value=settings['target_fps'],
            size_hint_y=None,
            height=40
        )
        
        def update_target_fps(slider):
            val = int(slider.value)
            target_fps_label.text = f'Target FPS: {val}'
            self.settings_manager.update_app_setting(app_name, 'target_fps', val)
        
        target_fps_slider.bind(value=update_target_fps)
        settings_layout.add_widget(target_fps_slider)
        
        # Refresh Rate Spinner
        refresh_label = Label(
            text='Refresh Rate (Hz):',
            size_hint_y=None,
            height=30
        )
        settings_layout.add_widget(refresh_label)
        
        refresh_spinner = Spinner(
            text=str(int(settings['refresh_rate'])),
            values=['30', '60', '90', '120', '144'],
            size_hint_y=None,
            height=50
        )
        
        def update_refresh(spinner):
            val = int(spinner.text)
            self.settings_manager.update_app_setting(app_name, 'refresh_rate', val)
        
        refresh_spinner.bind(text=update_refresh)
        settings_layout.add_widget(refresh_spinner)
        
        scroll.add_widget(settings_layout)
        content.add_widget(scroll)
        
        # Close button
        close_btn = Button(text='Close', size_hint_y=0.1, background_color=(0.8, 0.2, 0.2, 1))
        
        popup = Popup(
            title=f'Settings',
            content=content,
            size_hint=(0.9, 0.9),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        
        popup.open()


if __name__ == '__main__':
    VRSettingsApp().run()
