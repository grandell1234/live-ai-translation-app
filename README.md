# live-ai-translation-app
An application that combines OpenAI's GPT, Whisper, and TTS models to create a live translation application.

## Installation Instructions
Install the application:

```$ git clone https://github.com/grandell1234/live-ai-translation-app```

Ender folder:

```$ cd live-ai-translation-app```

Install dependencies:

```$ python3 -m pip install openai sounddevice numpy scipy pydub```

## Use Instructions
* Make sure you have an OpenAI API key in your environment variables.

* Uncomment the first section in the ```translator.py``` to get all your audio devices printed out. Below you can modify the variable provided to set it to whichever audio device you prefer (this is for Microphone, whatever Audio device is selected for your computer will be used for that.)
___
You can now run it with: 

```$ python3 translator.py```

___
