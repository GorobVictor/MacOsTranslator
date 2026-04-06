import json
import os
import subprocess
import sys
import time
from pathlib import Path

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

def get_resource_path(filename: str):
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, filename)

def get_config_path():
    if getattr(sys, "frozen", False):
        app_support_dir = Path.home() / "Library" / "Application Support" / "MacOsTranslator"
        app_support_dir.mkdir(parents=True, exist_ok=True)
        return app_support_dir / "config.json"
    return Path(os.path.dirname(__file__)) / "config.json"

def ensure_config_exists():
    config_path = get_config_path()
    if config_path.exists():
        return config_path

    default_config_path = Path(get_resource_path("config.json"))
    if default_config_path.exists():
        config_path.write_text(default_config_path.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        config_path.write_text(
            json.dumps(
                {
                    "openai_api_key": "",
                    "model": "gpt-5.4-nano",
                    "prompt": "Ти маєш перекладати те що я тобі скину. З української на англійську, або навпаки."
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    return config_path

def load_config():
    config_path = ensure_config_exists()
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def translate_text(text: str):
    config = load_config()
    client = OpenAI(
        api_key=config.get("openai_api_key"),
    )

    response = client.responses.create(
        model=config.get("model"),
        instructions=config.get("prompt"),
        input=text
    )

    return response.output_text.strip()

class TranslatorApp(rumps.App):
    def __init__(self):
        super().__init__("AI Translator", icon=get_resource_path("icon.png"), quit_button=None)
        self.menu = ["Редагувати config.json", "Вийти"]
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

    @rumps.clicked("Редагувати config.json")
    def edit_config(self, _):
        config_path = ensure_config_exists()
        try:
            subprocess.Popen(["open", "-a", "TextEdit", str(config_path)])
        except Exception as e:
            show_dialog(f"Не вдалося відкрити config.json: {e}")

    @rumps.clicked("Вийти")
    def quit_app(self, _):
        rumps.quit_application()


if __name__ == "__main__":
    TranslatorApp().run()
