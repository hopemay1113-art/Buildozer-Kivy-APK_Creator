from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import json
import os
import time
import math
import struct
import wave
import numpy as np
from scipy import signal
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
                'refresh_rate': 60,
                'resolution_scale': 1.0,
                'graphics_quality': 'high',
                'motion_smoothing': 'on',
                'ambient_occlusion': 'off',
                'shadow_quality': 'medium',
                'texture_quality': 'high',
                'anti_aliasing': 'fxaa',
                'memory_limit': 2048,
                'touch_sensitivity': 1.0,
                'haptic_feedback': 'on',
                'frame_timing': 'adaptive',
                'power_profile': 'balanced',
                'cpu_threads': 4,
                'gpu_boost': 'off',
                'memory_compression': 'on',
            }
            self.save_settings()
        return self.settings[app_name]
    
    def update_app_setting(self, app_name, key, value):
        """Update a setting for an app."""
        if app_name not in self.settings:
            self.settings[app_name] = {}
        self.settings[app_name][key] = value
        self.save_settings()


class SoundBoard:
    """Manages soundboard sounds with customization."""
    
    def __init__(self):
        self.sounds = {
            'beep': {'path': self.create_beep_sound(), 'volume': 0.7, 'pitch': 1.0},
            'success': {'path': self.create_success_sound(), 'volume': 0.7, 'pitch': 1.0},
            'error': {'path': self.create_error_sound(), 'volume': 0.7, 'pitch': 1.0},
            'click': {'path': self.create_click_sound(), 'volume': 0.7, 'pitch': 1.0},
            'notification': {'path': self.create_notification_sound(), 'volume': 0.6, 'pitch': 1.0},
            'alert': {'path': self.create_alert_sound(), 'volume': 0.8, 'pitch': 1.0},
            'chime': {'path': self.create_chime_sound(), 'volume': 0.5, 'pitch': 1.0},
            'laser': {'path': self.create_laser_sound(), 'volume': 0.6, 'pitch': 1.0},
        }
        self.current_sound = None
        self.master_volume = 1.0
    
    def create_beep_sound(self):
        """Create a simple beep sound file."""
        sound_file = os.path.join(os.path.expanduser('~'), 'beep.wav')
        if not os.path.exists(sound_file):
            try:
                sample_rate = 44100
                duration = 0.5
                frequency = 800
                
                num_samples = int(sample_rate * duration)
                frames = []
                
                for i in range(num_samples):
                    sample = int(32767 * 0.5 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
                    frames.append(struct.pack('<h', sample))
                
                with wave.open(sound_file, 'w') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(b''.join(frames))
            except:
                pass
        return sound_file
    
    def create_success_sound(self):
        """Create a success sound file."""
        sound_file = os.path.join(os.path.expanduser('~'), 'success.wav')
        if not os.path.exists(sound_file):
            try:
                sample_rate = 44100
                duration = 0.8
                
                num_samples = int(sample_rate * duration)
                frames = []
                
                # Two ascending tones
                for i in range(num_samples):
                    if i < num_samples // 2:
                        freq = 600
                    else:
                        freq = 900
                    sample = int(32767 * 0.3 * math.sin(2.0 * math.pi * freq * i / sample_rate))
                    frames.append(struct.pack('<h', sample))
                
                with wave.open(sound_file, 'w') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(b''.join(frames))
            except:
                pass
        return sound_file
    
    def create_error_sound(self):
        """Create an error sound file."""
        sound_file = os.path.join(os.path.expanduser('~'), 'error.wav')
        if not os.path.exists(sound_file):
            try:
                sample_rate = 44100
                duration = 0.6
                
                num_samples = int(sample_rate * duration)
                frames = []
                
                # Descending tones
                for i in range(num_samples):
                    if i < num_samples // 2:
                        freq = 300
                    else:
                        freq = 150
                    sample = int(32767 * 0.3 * math.sin(2.0 * math.pi * freq * i / sample_rate))
                    frames.append(struct.pack('<h', sample))
                
                with wave.open(sound_file, 'w') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(b''.join(frames))
            except:
                pass
        return sound_file
    
    def create_click_sound(self):
        """Create a click sound file."""
        sound_file = os.path.join(os.path.expanduser('~'), 'click.wav')
        if not os.path.exists(sound_file):
            try:
                sample_rate = 44100
                duration = 0.1
                frequency = 1000
                
                num_samples = int(sample_rate * duration)
                frames = []
                
                for i in range(num_samples):
                    # Envelope to make it click-like
                    env = 1.0 - (i / num_samples)
                    sample = int(32767 * 0.4 * env * math.sin(2.0 * math.pi * frequency * i / sample_rate))
                    frames.append(struct.pack('<h', sample))
                
                with wave.open(sound_file, 'w') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    wav_file.writeframes(b''.join(frames))
            except:
                pass
        return sound_file
        """Play a sound by name."""
        try:
            if self.current_sound:
                self.current_sound.stop()
            
            if sound_name in self.sounds:
                sound_file = self.sounds[sound_name]
                self.current_sound = SoundLoader.load(sound_file)
                if self.current_sound:
                    self.current_sound.play()
        except Exception as e:
            print(f"Error playing sound: {e}")
    
    def stop_sound(self):
        """Stop current sound."""
        if self.current_sound:
            self.current_sound.stop()
            self.current_sound = None


class VoiceChanger:
    """Manages real-time voice changing."""
    
    def __init__(self):
        self.is_recording = False
        self.pitch_shift = 0  # semitones
        self.speed = 1.0  # playback speed
        self.volume = 0.7  # volume level
        self.recording_thread = None
        self.audio_buffer = []
        self.sample_rate = 44100
    
    def shift_pitch(self, audio_data, semitones):
        """Shift pitch of audio data."""
        try:
            if semitones == 0:
                return audio_data
            
            # Convert to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
            
            # Calculate pitch shift factor
            factor = 2.0 ** (semitones / 12.0)
            
            # Simple pitch shifting using linear interpolation
            original_length = len(audio_array)
            new_length = int(original_length / factor)
            
            if new_length <= 0:
                return audio_data
            
            # Resample using scipy
            indices = np.linspace(0, original_length - 1, new_length)
            shifted = np.interp(indices, np.arange(original_length), audio_array)
            
            # Pad or trim to original length
            if len(shifted) < original_length:
                shifted = np.pad(shifted, (0, original_length - len(shifted)))
            else:
                shifted = shifted[:original_length]
            
            return shifted.astype(np.int16).tobytes()
        except:
            return audio_data
    
    def change_speed(self, audio_data, speed_factor):
        """Change speed of audio."""
        try:
            if speed_factor == 1.0:
                return audio_data
            
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
            original_length = len(audio_array)
            new_length = int(original_length / speed_factor)
            
            if new_length <= 0:
                return audio_data
            
            indices = np.linspace(0, original_length - 1, new_length)
            changed = np.interp(indices, np.arange(original_length), audio_array)
            
            if len(changed) < original_length:
                changed = np.pad(changed, (0, original_length - len(changed)))
            else:
                changed = changed[:original_length]
            
            return changed.astype(np.int16).tobytes()
        except:
            return audio_data
    
    def apply_reverb(self, audio_data, decay=0.5):
        """Apply simple reverb effect."""
        try:
            audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32)
            
            delay_samples = int(self.sample_rate * 0.05)  # 50ms delay
            if len(audio_array) < delay_samples:
                return audio_data
            
            delayed = np.concatenate([np.zeros(delay_samples), audio_array[:-delay_samples]])
            reverb = audio_array + decay * delayed
            reverb = np.clip(reverb, -32768, 32767)
            
            return reverb.astype(np.int16).tobytes()
        except:
            return audio_data


class CynEnhancementsApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.settings_manager = AppSettingsManager()
        self.soundboard = SoundBoard()
        self.voice_changer = VoiceChanger()
        self.current_app = None
    
    def build(self):
        Window.size = (400, 800)
        self.title = 'Cyn Enhancements'
        
        # Main tabbed interface
        tab_panel = TabbedPanel(do_default_tab=False)
        
        # Settings Tab
        settings_tab = TabbedPanelItem(text='Settings')
        settings_tab.content = self.build_settings_tab()
        tab_panel.add_widget(settings_tab)
        
        # Soundboard Tab
        soundboard_tab = TabbedPanelItem(text='Soundboard')
        soundboard_tab.content = self.build_soundboard_tab()
        tab_panel.add_widget(soundboard_tab)
        
        # Voice Changer Tab
        voice_tab = TabbedPanelItem(text='Voice')
        voice_tab.content = self.build_voice_changer_tab()
        tab_panel.add_widget(voice_tab)
        
        tab_panel.default_tab = settings_tab
        
        return tab_panel
    
    def build_settings_tab(self):
        """Build the settings management tab."""
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = Label(text='App Settings', size_hint_y=0.1, font_size='20sp', bold=True)
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
    
    def build_soundboard_tab(self):
        """Build the soundboard tab."""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = Label(text='Sound Effects', size_hint_y=0.1, font_size='20sp', bold=True)
        layout.add_widget(header)
        
        # Sound buttons
        sounds_layout = GridLayout(cols=2, spacing=10, size_hint_y=0.7, padding=10)
        
        sounds = [
            ('🔔 Beep', 'beep', (0.2, 0.6, 0.8, 1)),
            ('✓ Success', 'success', (0.2, 0.8, 0.4, 1)),
            ('✕ Error', 'error', (0.8, 0.2, 0.2, 1)),
            ('• Click', 'click', (0.6, 0.6, 0.2, 1)),
        ]
        
        for label, sound_name, color in sounds:
            btn = Button(
                text=label,
                background_color=color,
                font_size='16sp'
            )
            btn.bind(on_press=lambda x, s=sound_name: self.play_sound(s))
            sounds_layout.add_widget(btn)
        
        layout.add_widget(sounds_layout)
        
        # Stop button
        stop_btn = Button(
            text='Stop Sound',
            size_hint_y=0.15,
            background_color=(0.5, 0.5, 0.5, 1),
            font_size='16sp'
        )
        stop_btn.bind(on_press=self.stop_sound)
        layout.add_widget(stop_btn)
        
        # Info
        info = Label(
            text='Tap buttons to play sounds\nThey play through device audio',
            size_hint_y=0.1,
            font_size='12sp',
            color=(0.7, 0.7, 0.7, 1)
        )
        layout.add_widget(info)
        
        return layout
    
    def play_sound(self, sound_name):
        """Play a sound from soundboard."""
        self.soundboard.play_sound(sound_name)
    
    def stop_sound(self, instance):
        """Stop current sound."""
        self.soundboard.stop_sound()
    
    def build_voice_changer_tab(self):
        """Build the voice changer tab."""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Header
        header = Label(text='Live Voice Changer', size_hint_y=0.08, font_size='18sp', bold=True)
        layout.add_widget(header)
        
        # Controls scroll
        scroll = ScrollView()
        controls_layout = GridLayout(cols=1, spacing=15, size_hint_y=None, padding=10)
        controls_layout.bind(minimum_height=controls_layout.setter('height'))
        
        # Pitch Control
        pitch_label = Label(text='Pitch: 0 semitones', size_hint_y=None, height=30, font_size='14sp')
        controls_layout.add_widget(pitch_label)
        
        pitch_slider = Slider(
            min=-12,
            max=12,
            value=0,
            size_hint_y=None,
            height=40
        )
        
        def update_pitch(slider):
            val = int(slider.value)
            pitch_label.text = f'Pitch: {val} semitones'
            self.voice_changer.pitch_shift = val
        
        pitch_slider.bind(value=update_pitch)
        controls_layout.add_widget(pitch_slider)
        
        # Speed Control
        speed_label = Label(text='Speed: 1.0x', size_hint_y=None, height=30, font_size='14sp')
        controls_layout.add_widget(speed_label)
        
        speed_slider = Slider(
            min=0.5,
            max=2.0,
            value=1.0,
            size_hint_y=None,
            height=40
        )
        
        def update_speed(slider):
            val = round(slider.value, 2)
            speed_label.text = f'Speed: {val}x'
            self.voice_changer.speed = val
        
        speed_slider.bind(value=update_speed)
        controls_layout.add_widget(speed_slider)
        
        # Volume Control
        volume_label = Label(text='Volume: 70%', size_hint_y=None, height=30, font_size='14sp')
        controls_layout.add_widget(volume_label)
        
        volume_slider = Slider(
            min=0,
            max=1,
            value=0.7,
            size_hint_y=None,
            height=40
        )
        
        def update_volume(slider):
            val = int(slider.value * 100)
            volume_label.text = f'Volume: {val}%'
            self.voice_changer.volume = slider.value
        
        volume_slider.bind(value=update_volume)
        controls_layout.add_widget(volume_slider)
        
        # Reverb toggle
        reverb_label = Label(text='Effects', size_hint_y=None, height=30, font_size='14sp')
        controls_layout.add_widget(reverb_label)
        
        effects_spinner = Spinner(
            text='None',
            values=['None', 'Reverb', 'Echo'],
            size_hint_y=None,
            height=50
        )
        controls_layout.add_widget(effects_spinner)
        
        scroll.add_widget(controls_layout)
        layout.add_widget(scroll)
        
        # Control buttons
        button_layout = BoxLayout(size_hint_y=0.15, spacing=10, padding=10)
        
        record_btn = Button(
            text='🎤 Start\nRecording',
            background_color=(0.2, 0.7, 0.2, 1),
            font_size='14sp'
        )
        record_btn.bind(on_press=self.start_voice_recording)
        button_layout.add_widget(record_btn)
        
        stop_btn = Button(
            text='⏹ Stop\nRecording',
            background_color=(0.7, 0.2, 0.2, 1),
            font_size='14sp'
        )
        stop_btn.bind(on_press=self.stop_voice_recording)
        button_layout.add_widget(stop_btn)
        
        layout.add_widget(button_layout)
        
        return layout
    
    def start_voice_recording(self, instance):
        """Start voice recording."""
        self.voice_changer.is_recording = True
        instance.text = '🎤 Recording...'
        instance.disabled = True
    
    def stop_voice_recording(self, instance):
        """Stop voice recording."""
        self.voice_changer.is_recording = False
    
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
    CynEnhancementsApp().run()
