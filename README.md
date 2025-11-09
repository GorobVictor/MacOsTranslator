# MacOsTranslator

1. Change api key in config.json
2. Run build command
    ```commandline
    pyinstaller --noconsole --windowed --name "MacOsTranslator" --icon=icon.png --add-data "icon.png:." --add-data "config.json:." main.py
    ```
3. Add these lines to info.plist in .app build
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