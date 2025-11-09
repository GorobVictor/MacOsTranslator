import json
import os
import subprocess
import sys
import time

import osascript
import rumps
from openai import OpenAI
from pynput import keyboard

cmd_pressed = False
last_press = 0

def show_dialog(text):
    safe_text = text.replace("\\", "\\\\").replace('"', '\\"')

    script = f'display dialog "{safe_text}" buttons {{"OK"}} default button "OK" with title "Переклад."'

    try:
        osascript.run(script)
    except Exception as e:
        print("Помилка при показі діалогу:", e)

def load_config():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    config_path = os.path.join(base_path, "config.json")
    with open(config_path, "r") as f:
        return json.load(f)

def translate_text(text: str):
    config = load_config()
    client = OpenAI(
        api_key=config.get("openai_api_key"),
    )

    prompt = f"Translate:\n\n{text}"

    response = client.responses.create(
        model="gpt-4.1-nano",
        instructions="You are a helpful translator who automatically detects the language of the text and translates it into Ukrainian, and if the text is in Ukrainian, you translate it into English.",
        input=prompt
    )

    return response.output_text.strip()

class TranslatorApp(rumps.App):
    def __init__(self):
        super().__init__("AI Translator", icon="icon.png", quit_button=None)
        self.menu = ["Вийти"]
        self.key_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.key_listener.start()

    def on_press(self, key):
        global cmd_pressed, last_press
        if key == keyboard.Key.cmd:
            cmd_pressed = True
        elif key == keyboard.KeyCode.from_char('c') and cmd_pressed:
            now = time.time()
            if now - last_press < 0.5:
                text = subprocess.check_output(["pbpaste"]).decode("utf-8").strip()
                translated_text = translate_text(text)
                if text:
                    show_dialog(translated_text)
            last_press = now

    def on_release(self, key):
        global cmd_pressed
        if key == keyboard.Key.cmd:
            cmd_pressed = False

    @rumps.clicked("Вийти")
    def quit_app(self, _):
        rumps.quit_application()


if __name__ == "__main__":
    TranslatorApp().run()
