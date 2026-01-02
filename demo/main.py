from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label


class DemoApp(App):
    def build(self):
        self.counter = 0
        
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title label
        title = Label(text='Counter App', size_hint_y=0.2, font_size='24sp')
        layout.add_widget(title)
        
        # Counter display
        self.counter_label = Label(text='Count: 0', size_hint_y=0.3, font_size='32sp')
        layout.add_widget(self.counter_label)
        
        # Button layout
        button_layout = BoxLayout(size_hint_y=0.3, spacing=10)
        
        # Decrement button
        dec_button = Button(text='−', font_size='24sp')
        dec_button.bind(on_press=self.decrement)
        button_layout.add_widget(dec_button)
        
        # Increment button
        inc_button = Button(text='+', font_size='24sp')
        inc_button.bind(on_press=self.increment)
        button_layout.add_widget(inc_button)
        
        # Reset button
        reset_button = Button(text='Reset', font_size='18sp')
        reset_button.bind(on_press=self.reset)
        button_layout.add_widget(reset_button)
        
        layout.add_widget(button_layout)
        
        return layout
    
    def increment(self, instance):
        self.counter += 1
        self.counter_label.text = f'Count: {self.counter}'
    
    def decrement(self, instance):
        self.counter -= 1
        self.counter_label.text = f'Count: {self.counter}'
    
    def reset(self, instance):
        self.counter = 0
        self.counter_label.text = 'Count: 0'


if __name__ == '__main__':
    DemoApp().run()
