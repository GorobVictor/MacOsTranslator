run build command

```commandline
pyinstaller --noconsole --windowed --name "MacOsTranslator" --icon=icon.png --add-data "icon.png:." --add-data "config.json:." main.py
```

need to add icon.png to `dist/AI Translator.app/Contents/Frameworks/`
```
    <key>LSUIElement</key>
    <string>1</string>
    <key>LSEnvironment</key>
    <dict>
        <key>LANG</key>
        <string>en_US.UTF-8</string>
        <key>LC_ALL</key>
        <string>en_US.UTF-8</string>
    </dict>
```