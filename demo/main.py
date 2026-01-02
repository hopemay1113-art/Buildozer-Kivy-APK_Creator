from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
import json
import os
import math
import struct
import wave
import array
import threading

# Request Android permissions
try:
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.QUERY_ALL_PACKAGES,
        Permission.READ_EXTERNAL_STORAGE,
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.RECORD_AUDIO,
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
    """Manages comprehensive app settings."""
    
    DEFAULT_SETTINGS = {
        'fps_cap': 60,
        'target_fps': 60,
        'refresh_rate': 60,
        'resolution_scale': 1.0,
        'graphics_quality': 'high',
        'motion_smoothing': True,
        'ambient_occlusion': False,
        'shadow_quality': 'medium',
        'texture_quality': 'high',
        'anti_aliasing': 'fxaa',
        'memory_limit': 2048,
        'touch_sensitivity': 1.0,
        'haptic_feedback': True,
        'frame_timing': 'adaptive',
        'power_profile': 'balanced',
        'cpu_threads': 4,
        'gpu_boost': False,
        'memory_compression': True,
        'vsync': True,
        'cpu_governor': 'schedutil',
        'gpu_frequency': 'auto',
    }
    
    def __init__(self):
        self.settings_file = os.path.join(os.path.expanduser('~'), 'app_settings.json')
        self.settings = self.load_settings()
    
    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get_app_settings(self, app_name):
        if app_name not in self.settings:
            self.settings[app_name] = self.DEFAULT_SETTINGS.copy()
            self.save_settings()
        return self.settings[app_name]
    
    def update_app_setting(self, app_name, key, value):
        if app_name not in self.settings:
            self.settings[app_name] = self.DEFAULT_SETTINGS.copy()
        self.settings[app_name][key] = value
        self.save_settings()


class SoundBoardManager:
    """Enhanced soundboard with customization."""
    
    SOUND_TEMPLATES = {
        'beep': {'freq': 800, 'duration': 0.5, 'volume': 0.7},
        'success': {'freq': [600, 900], 'duration': 0.8, 'volume': 0.7},
        'error': {'freq': [300, 150], 'duration': 0.6, 'volume': 0.7},
        'click': {'freq': 1000, 'duration': 0.1, 'volume': 0.7},
        'notification': {'freq': [500, 700, 900], 'duration': 0.4, 'volume': 0.6},
        'alert': {'freq': 'sweep', 'duration': 0.5, 'volume': 0.8},
        'chime': {'freq': 1200, 'duration': 0.6, 'volume': 0.5},
        'laser': {'freq': 'down', 'duration': 0.2, 'volume': 0.6},
        'pop': {'freq': 150, 'duration': 0.15, 'volume': 0.5},
        'whoosh': {'freq': 'sweep', 'duration': 0.3, 'volume': 0.6},
    }
    
    def __init__(self):
        self.sounds = {}
        self.sound_config = {}
        self.master_volume = 1.0
        self.current_sound = None
        self.sample_rate = 44100
        self._generate_all_sounds()
    
    def _generate_all_sounds(self):
        """Generate all sound files."""
        for name, config in self.SOUND_TEMPLATES.items():
            path = self._create_sound(name, config)
            self.sounds[name] = path
            self.sound_config[name] = {
                'volume': config['volume'],
                'pitch': 1.0,
                'enabled': True,
                'loop': False
            }
    
    def _create_sound(self, name, config):
        """Create a sound file."""
        sound_file = os.path.join(os.path.expanduser('~'), f'{name}.wav')
        if not os.path.exists(sound_file):
            try:
                sample_rate = 44100
                duration = config.get('duration', 0.5)
                num_samples = int(sample_rate * duration)
                frames = []
                
                if config['freq'] == 'sweep':
                    for i in range(num_samples):
                        env = 1.0 - (i / num_samples) * 0.8
                        freq = 2000 - 1500 * (i / num_samples)
                        sample = int(32767 * 0.4 * env * math.sin(2.0 * math.pi * freq * i / sample_rate))
                        frames.append(struct.pack('<h', sample))
                elif config['freq'] == 'down':
                    for i in range(num_samples):
                        env = 1.0 - (i / num_samples)
                        freq = 2000 - 1500 * (i / num_samples)
                        sample = int(32767 * 0.4 * env * math.sin(2.0 * math.pi * freq * i / sample_rate))
                        frames.append(struct.pack('<h', sample))
                elif isinstance(config['freq'], list):
                    for i in range(num_samples):
                        idx = int((i / num_samples) * (len(config['freq']) - 1))
                        freq = config['freq'][idx]
                        sample = int(32767 * 0.3 * math.sin(2.0 * math.pi * freq * i / sample_rate))
                        frames.append(struct.pack('<h', sample))
                else:
                    for i in range(num_samples):
                        freq = config['freq']
                        sample = int(32767 * 0.5 * math.sin(2.0 * math.pi * freq * i / sample_rate))
                        frames.append(struct.pack('<h', sample))
                
                with wave.open(sound_file, 'w') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(b''.join(frames))
            except:
                pass
        return sound_file
    
    def play_sound(self, sound_name):
        try:
            if self.current_sound:
                self.current_sound.stop()
            
            config = self.sound_config.get(sound_name, {})
            if not config.get('enabled', True):
                return
            
            sound_file = self.sounds.get(sound_name)
            if sound_file:
                self.current_sound = SoundLoader.load(sound_file)
                if self.current_sound:
                    self.current_sound.volume = config.get('volume', 0.7) * self.master_volume
                    self.current_sound.play()
        except Exception as e:
            print(f"Error playing sound: {e}")
    
    def stop_sound(self):
        if self.current_sound:
            self.current_sound.stop()
            self.current_sound = None
    
    def set_sound_volume(self, sound_name, volume):
        if sound_name in self.sound_config:
            self.sound_config[sound_name]['volume'] = volume
    
    def set_master_volume(self, volume):
        self.master_volume = volume


class VoiceChangerEngine:
    """Advanced voice changer with EQ and presets."""
    
    VOICE_PRESETS = {
        'normal': {'pitch': 0, 'speed': 1.0, 'bass': 0, 'mid': 0, 'treble': 0},
        'high': {'pitch': 12, 'speed': 1.0, 'bass': -5, 'mid': 0, 'treble': 5},
        'deep': {'pitch': -12, 'speed': 1.0, 'bass': 5, 'mid': -3, 'treble': -5},
        'fast': {'pitch': 0, 'speed': 1.3, 'bass': 0, 'mid': 2, 'treble': 0},
        'slow': {'pitch': 0, 'speed': 0.7, 'bass': 2, 'mid': 0, 'treble': -2},
        'robotic': {'pitch': 0, 'speed': 1.0, 'bass': 5, 'mid': -10, 'treble': 5},
        'chipmunk': {'pitch': 24, 'speed': 1.1, 'bass': -8, 'mid': 0, 'treble': 8},
        'demon': {'pitch': -24, 'speed': 0.9, 'bass': 10, 'mid': -5, 'treble': -8},
    }
    
    def __init__(self):
        self.is_recording = False
        self.pitch_shift = 0
        self.speed = 1.0
        self.volume = 0.7
        self.bass = 0
        self.mid = 0
        self.treble = 0
        self.reverb_amount = 0.0
        self.echo_amount = 0.0
        self.distortion = 0.0
        self.current_preset = 'normal'
        self.sample_rate = 44100
    
    def apply_preset(self, preset_name):
        if preset_name in self.VOICE_PRESETS:
            preset = self.VOICE_PRESETS[preset_name]
            self.pitch_shift = preset['pitch']
            self.speed = preset['speed']
            self.bass = preset['bass']
            self.mid = preset['mid']
            self.treble = preset['treble']
            self.current_preset = preset_name
    
    def apply_equalizer(self, audio_data):
        """Apply EQ adjustments using pure Python."""
        try:
            if self.bass == 0 and self.mid == 0 and self.treble == 0:
                return audio_data
            
            # Convert bytes to samples
            audio_array = array.array('h')
            audio_array.frombytes(audio_data)
            
            # Apply EQ by scaling amplitude
            eq_factor = 1.0
            if self.bass != 0:
                eq_factor *= (1.0 + self.bass / 100.0)
            if self.mid != 0:
                eq_factor *= (1.0 + self.mid / 100.0)
            if self.treble != 0:
                eq_factor *= (1.0 + self.treble / 100.0)
            
            # Apply factor and clamp to int16 range
            result = array.array('h')
            for sample in audio_array:
                scaled = int(sample * eq_factor)
                # Clamp to int16 range [-32768, 32767]
                clamped = max(-32768, min(32767, scaled))
                result.append(clamped)
            
            return result.tobytes()
        except:
            return audio_data
    
    def apply_distortion(self, audio_data):
        """Apply distortion effect using pure Python."""
        if self.distortion == 0:
            return audio_data
        
        try:
            # Convert bytes to samples
            audio_array = array.array('h')
            audio_array.frombytes(audio_data)
            
            # Calculate threshold for distortion
            threshold = int(32767 * (1.0 - self.distortion / 100.0))
            
            # Apply distortion (hard clipping)
            result = array.array('h')
            for sample in audio_array:
                if sample > threshold:
                    clamped = threshold
                elif sample < -threshold:
                    clamped = -threshold
                else:
                    clamped = sample
                result.append(clamped)
            
            return result.tobytes()
        except:
            return audio_data


class CynEnhancementsApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings_manager = AppSettingsManager()
        self.soundboard = SoundBoardManager()
        self.voice_engine = VoiceChangerEngine()
        self.current_app = None
    
    def build(self):
        Window.size = (400, 900)
        self.title = 'Cyn Enhancements'
        
        tab_panel = TabbedPanel(do_default_tab=False)
        
        settings_tab = TabbedPanelItem(text='Settings')
        settings_tab.content = self.build_settings_tab()
        tab_panel.add_widget(settings_tab)
        
        soundboard_tab = TabbedPanelItem(text='Soundboard')
        soundboard_tab.content = self.build_soundboard_tab()
        tab_panel.add_widget(soundboard_tab)
        
        voice_tab = TabbedPanelItem(text='Voice')
        voice_tab.content = self.build_voice_tab()
        tab_panel.add_widget(voice_tab)
        
        tab_panel.default_tab = settings_tab
        return tab_panel
    
    def build_settings_tab(self):
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        header = Label(text='App Settings', size_hint_y=0.1, font_size='20sp', bold=True)
        main_layout.add_widget(header)
        
        scroll_view = ScrollView(size_hint=(1, 0.9))
        self.apps_grid = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.apps_grid.bind(minimum_height=self.apps_grid.setter('height'))
        
        installed_apps = get_installed_apps()
        if not installed_apps:
            self.apps_grid.add_widget(Label(text='No apps found', size_hint_y=None, height=50))
        else:
            for app in installed_apps:
                btn = Button(text=app, size_hint_y=None, height=50, background_color=(0.2, 0.6, 0.8, 1))
                btn.bind(on_press=self.show_app_settings)
                self.apps_grid.add_widget(btn)
        
        scroll_view.add_widget(self.apps_grid)
        main_layout.add_widget(scroll_view)
        return main_layout
    
    def show_app_settings(self, instance):
        app_name = instance.text
        settings = self.settings_manager.get_app_settings(app_name)
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        title = Label(text=f'Settings: {app_name}', size_hint_y=0.12, font_size='16sp', bold=True)
        content.add_widget(title)
        
        scroll = ScrollView()
        settings_layout = GridLayout(cols=1, spacing=12, size_hint_y=None, padding=10)
        settings_layout.bind(minimum_height=settings_layout.setter('height'))
        
        # FPS Controls
        settings_layout.add_widget(Label(text='Performance', size_hint_y=None, height=25, bold=True))
        
        for key in ['fps_cap', 'target_fps', 'refresh_rate']:
            label = Label(text=f'{key}: {int(settings[key])}', size_hint_y=None, height=30)
            settings_layout.add_widget(label)
            slider = Slider(min=30, max=240, value=settings[key], size_hint_y=None, height=40)
            
            def update_val(s, k=key, l=label, app=app_name):
                val = int(s.value)
                l.text = f'{k}: {val}'
                self.settings_manager.update_app_setting(app, k, val)
            
            slider.bind(value=update_val)
            settings_layout.add_widget(slider)
        
        # Graphics
        settings_layout.add_widget(Label(text='Graphics', size_hint_y=None, height=25, bold=True))
        
        for key in ['resolution_scale', 'shadow_quality', 'texture_quality']:
            label = Label(text=f'{key}: {settings[key]}', size_hint_y=None, height=30)
            settings_layout.add_widget(label)
            
            if key == 'resolution_scale':
                slider = Slider(min=0.5, max=1.5, value=settings[key], size_hint_y=None, height=40)
                def update_res(s, l=label, app=app_name):
                    val = round(s.value, 2)
                    l.text = f'resolution_scale: {val}'
                    self.settings_manager.update_app_setting(app, 'resolution_scale', val)
                slider.bind(value=update_res)
            else:
                spinner = Spinner(
                    text=settings[key],
                    values=['low', 'medium', 'high', 'ultra'],
                    size_hint_y=None,
                    height=50
                )
                def update_spinner(s, k=key, app=app_name):
                    self.settings_manager.update_app_setting(app, k, s.text)
                spinner.bind(text=update_spinner)
                settings_layout.add_widget(spinner)
                continue
            
            settings_layout.add_widget(slider)
        
        # System
        settings_layout.add_widget(Label(text='System', size_hint_y=None, height=25, bold=True))
        
        for key in ['memory_limit', 'touch_sensitivity']:
            label = Label(text=f'{key}: {settings[key]}', size_hint_y=None, height=30)
            settings_layout.add_widget(label)
            slider = Slider(
                min=1024 if key == 'memory_limit' else 0.5,
                max=4096 if key == 'memory_limit' else 2.0,
                value=settings[key],
                size_hint_y=None,
                height=40
            )
            
            def update_sys(s, k=key, l=label, app=app_name):
                val = int(s.value) if k == 'memory_limit' else round(s.value, 2)
                l.text = f'{k}: {val}'
                self.settings_manager.update_app_setting(app, k, val)
            
            slider.bind(value=update_sys)
            settings_layout.add_widget(slider)
        
        # Toggles
        settings_layout.add_widget(Label(text='Features', size_hint_y=None, height=25, bold=True))
        
        for key in ['motion_smoothing', 'haptic_feedback', 'vsync', 'gpu_boost']:
            row = BoxLayout(size_hint_y=None, height=50, spacing=10)
            row.add_widget(Label(text=key, size_hint_x=0.7))
            switch = Switch(active=settings[key], size_hint_x=0.3)
            
            def update_toggle(s, k=key, app=app_name):
                self.settings_manager.update_app_setting(app, k, s.active)
            
            switch.bind(active=update_toggle)
            row.add_widget(switch)
            settings_layout.add_widget(row)
        
        scroll.add_widget(settings_layout)
        content.add_widget(scroll)
        
        close_btn = Button(text='Close', size_hint_y=0.08, background_color=(0.8, 0.2, 0.2, 1))
        popup = Popup(title='Settings', content=content, size_hint=(0.95, 0.95))
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.open()
    
    def build_soundboard_tab(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        header = Label(text='Sound Effects', size_hint_y=0.08, font_size='18sp', bold=True)
        layout.add_widget(header)
        
        scroll = ScrollView()
        grid = GridLayout(cols=2, spacing=10, size_hint_y=None, padding=10)
        grid.bind(minimum_height=grid.setter('height'))
        
        for name in self.soundboard.SOUND_TEMPLATES.keys():
            btn = Button(text=name.title(), background_color=(0.2, 0.6, 0.8, 1), size_hint_y=None, height=60)
            btn.bind(on_press=lambda x, s=name: self.soundboard.play_sound(s))
            grid.add_widget(btn)
        
        scroll.add_widget(grid)
        layout.add_widget(scroll)
        
        # Master volume
        vol_layout = BoxLayout(size_hint_y=0.12, spacing=10, padding=10)
        vol_layout.add_widget(Label(text='Master:', size_hint_x=0.2))
        master_vol = Slider(min=0, max=1, value=0.7, size_hint_x=0.8)
        master_vol.bind(value=lambda s: self.soundboard.set_master_volume(s.value))
        vol_layout.add_widget(master_vol)
        layout.add_widget(vol_layout)
        
        return layout
    
    def build_voice_tab(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        header = Label(text='Voice Changer', size_hint_y=0.08, font_size='18sp', bold=True)
        layout.add_widget(header)
        
        scroll = ScrollView()
        controls = GridLayout(cols=1, spacing=15, size_hint_y=None, padding=10)
        controls.bind(minimum_height=controls.setter('height'))
        
        # Presets
        controls.add_widget(Label(text='Voice Presets:', size_hint_y=None, height=25, bold=True))
        preset_spinner = Spinner(
            text='Normal',
            values=list(self.voice_engine.VOICE_PRESETS.keys()),
            size_hint_y=None,
            height=50
        )
        preset_spinner.bind(text=lambda s: self.voice_engine.apply_preset(s.text.lower()))
        controls.add_widget(preset_spinner)
        
        # Pitch
        controls.add_widget(Label(text='Pitch (semitones):', size_hint_y=None, height=25))
        pitch_label = Label(text='0', size_hint_y=None, height=30)
        controls.add_widget(pitch_label)
        pitch_slider = Slider(min=-24, max=24, value=0, size_hint_y=None, height=40)
        pitch_slider.bind(value=lambda s: (setattr(self.voice_engine, 'pitch_shift', int(s.value)), pitch_label.__setattr__('text', str(int(s.value)))))
        controls.add_widget(pitch_slider)
        
        # Speed
        controls.add_widget(Label(text='Speed:', size_hint_y=None, height=25))
        speed_label = Label(text='1.0x', size_hint_y=None, height=30)
        controls.add_widget(speed_label)
        speed_slider = Slider(min=0.5, max=2.0, value=1.0, size_hint_y=None, height=40)
        speed_slider.bind(value=lambda s: (setattr(self.voice_engine, 'speed', round(s.value, 2)), speed_label.__setattr__('text', f'{round(s.value, 2)}x')))
        controls.add_widget(speed_slider)
        
        # EQ - Bass
        controls.add_widget(Label(text='Bass:', size_hint_y=None, height=25))
        bass_label = Label(text='0', size_hint_y=None, height=30)
        controls.add_widget(bass_label)
        bass_slider = Slider(min=-20, max=20, value=0, size_hint_y=None, height=40)
        bass_slider.bind(value=lambda s: (setattr(self.voice_engine, 'bass', int(s.value)), bass_label.__setattr__('text', str(int(s.value)))))
        controls.add_widget(bass_slider)
        
        # EQ - Mid
        controls.add_widget(Label(text='Mid:', size_hint_y=None, height=25))
        mid_label = Label(text='0', size_hint_y=None, height=30)
        controls.add_widget(mid_label)
        mid_slider = Slider(min=-20, max=20, value=0, size_hint_y=None, height=40)
        mid_slider.bind(value=lambda s: (setattr(self.voice_engine, 'mid', int(s.value)), mid_label.__setattr__('text', str(int(s.value)))))
        controls.add_widget(mid_slider)
        
        # EQ - Treble
        controls.add_widget(Label(text='Treble:', size_hint_y=None, height=25))
        treble_label = Label(text='0', size_hint_y=None, height=30)
        controls.add_widget(treble_label)
        treble_slider = Slider(min=-20, max=20, value=0, size_hint_y=None, height=40)
        treble_slider.bind(value=lambda s: (setattr(self.voice_engine, 'treble', int(s.value)), treble_label.__setattr__('text', str(int(s.value)))))
        controls.add_widget(treble_slider)
        
        # Effects
        controls.add_widget(Label(text='Reverb:', size_hint_y=None, height=25))
        reverb_label = Label(text='0%', size_hint_y=None, height=30)
        controls.add_widget(reverb_label)
        reverb_slider = Slider(min=0, max=100, value=0, size_hint_y=None, height=40)
        reverb_slider.bind(value=lambda s: (setattr(self.voice_engine, 'reverb_amount', int(s.value)), reverb_label.__setattr__('text', f'{int(s.value)}%')))
        controls.add_widget(reverb_slider)
        
        controls.add_widget(Label(text='Distortion:', size_hint_y=None, height=25))
        distortion_label = Label(text='0%', size_hint_y=None, height=30)
        controls.add_widget(distortion_label)
        distortion_slider = Slider(min=0, max=100, value=0, size_hint_y=None, height=40)
        distortion_slider.bind(value=lambda s: (setattr(self.voice_engine, 'distortion', int(s.value)), distortion_label.__setattr__('text', f'{int(s.value)}%')))
        controls.add_widget(distortion_slider)
        
        scroll.add_widget(controls)
        layout.add_widget(scroll)
        
        return layout


if __name__ == '__main__':
    CynEnhancementsApp().run()
