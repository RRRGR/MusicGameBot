"rc" is a library for converting alphabet and hiragana. I'll register it to PyPI.<br>

ChatSource/dictionary.json is like this:
```
{"00000000000": "normal", "0000000000000001": "hard"}
```
Quiz/quizmode.json is like this:
```
{
  "00000000000": {
    "deemo": でぃーも
  },
  "00000000000001": {
    "arcaea": あーけあ
  }
}
```
If you want to host this bot, please delete cogs/IR.py and line 20 in MusicGameBot.py.
```
20 SPREADSHEET_KEY = getenv('SPREADSHEET_KEY')
```

Directory Structure

```
.
├── ChatSource
│   ├── dictionary.json
│   ├── enoutput.mp3
│   ├── enoutput.wav
│   ├── input.txt
│   ├── output.mp3
│   └── output.wav
├── MusicGameBot.py //start bot
├── Quiz
│   ├── arcaeaimage
│   ├── chunithmimage
│   ├── cytusimage
│   ├── deemoimage
│   ├── quizmode.json
│   ├── sdvximage
│   └── songlist.json
├── README.md
├── cogs //main functions
│   ├── Admin.py
│   ├── Downloader.py
│   ├── Gacha.py
│   ├── IR.py
│   ├── ManageDic.py
│   ├── OtherCommands.py
│   ├── Quiz.py
│   ├── ReadText.py
│   └── SearchInformation.py
├── rc //library for en↔jp
│   ├── __init__.py
│   ├── en2kana.json
│   ├── en2rome.json
│   ├── hangle2kana.json
│   ├── kana2en.json
│   ├── main.py
│   └── rome2kana.json
├── requirements.txt
└── spread-sheet-350909-94d641982b67.json
```