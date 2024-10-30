import os
import glob
import cv2
import numpy as np
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.utils import platform

if platform == 'android':
    from jnius import autoclass

    Environment = autoclass('android.os.Environment')
    Activity = autoclass('org.kivy.android.PythonActivity')

    def check_permissions():
        permissions = [
            'android.permission.READ_EXTERNAL_STORAGE',
            'android.permission.WRITE_EXTERNAL_STORAGE'
        ]
        for perm in permissions:
            if Activity.checkSelfPermission(perm) != 0:
                Activity.requestPermissions(permissions)

    check_permissions()

# Kivy UI Design
from kivy.lang import Builder

Builder.load_string("""
<ThumbnailImage@Image>:
    size_hint_y: None
    height: 100
    allow_stretch: True

<ThumbnailGrid@GridLayout>:
    cols: 1
    size_hint_y: None
    height: self.minimum_height

<ThumbnailSelector>:
    orientation: 'vertical'
    FileChooserIconView:
        id: filechooser
        on_selection: app.update_thumbnails(self.selection)
    Button:
        text: 'Convert Images'
        size_hint_y: None
        height: 50
        on_release: app.convert_images()
    ScrollView:
        size_hint: (1, 0.8)
        ThumbnailGrid:
            id: thumbnail_grid
""")

class ThumbnailSelector(BoxLayout):
    pass

class ThumbnailApp(App):
    def build(self):
        self.title = "Image Converter"
        return ThumbnailSelector()

    def update_thumbnails(self, selected_files):
        thumbnail_grid = self.root.ids.thumbnail_grid
        thumbnail_grid.clear_widgets()

        for file in selected_files:
            if file.lower().endswith(('.webp', '.png', '.jpg', '.jpeg')):
                thumbnail = ThumbnailImage(source=file)
                thumbnail_grid.add_widget(thumbnail)

    def convert_images(self):
        filechooser = self.root.ids.filechooser
        selected_files = filechooser.selection
        output_dir = os.path.join(Environment.getExternalStorageDirectory().getAbsolutePath(), 'ConvertedImages')

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for file in selected_files:
            if file.lower().endswith('.webp'):
                self.convert_webp_to_gif(file, output_dir)

    def convert_webp_to_gif(self, webp_path, output_dir):
        gif_path = os.path.join(output_dir, os.path.basename(webp_path).replace('.webp', '.gif'))
        cap = cv2.VideoCapture(webp_path)

        frames = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame)

        if frames:
            frames[0] = cv2.cvtColor(frames[0], cv2.COLOR_RGB2BGR)
            cv2.imwrite(gif_path, frames[0])  # Save first frame as GIF for now
            self.show_popup("Conversion Complete", f"Saved to {gif_path}")

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()

if __name__ == '__main__':
    ThumbnailApp().run()
