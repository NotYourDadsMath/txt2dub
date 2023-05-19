txt2dub
=======

A text-based UI application for editing voiceover scripts and generating text to speech performances.

## What is `txt2dub` for?

`txt2dub` is a video content creation tool for writing scripts and generating overdub performances as MP3 files that can be imported into your video editing software. This supports a workflow for arranging video assets on your timeline based on the voice performance's timing. You can record your own voiceovers to replace the robotic text-to-speech performance, or you can keep the placeholders if that's the style you're targeting.

![Screenshot of txt2dub being used to edit a script with a quote from Frank Herbert's Dune](https://raw.githubusercontent.com/NotYourDadsMath/txt2dub/main/images/txt2dub-editing.png)


This is how it looks to edit a script in `txt2dub`. As you type each script line is played aloud by the text-to-speech system. You can play back a line, reorder lines or insert new lines anywhere in the script. You can set the voice performer and the rate of speech for each line in the script. You can undo or redo actions without limit. You can also play back the whole script starting from the selected line.

![Screenshot of txt2dub home screen](https://raw.githubusercontent.com/NotYourDadsMath/txt2dub/main/images/txt2dub-home-screen.png)

And here is the home screen.

## Who is `txt2dub` for?

`txt2dub` is designed to be easily installable on the major desktop platforms (Windows, Mac and Linux) without programming skills. More detailed installation instructions will be posted soon. For those familiar with Python, you can install `txt2dub` in a virtual environment or globally with:

```bash
pip install txt2dub
```

It can be run from its installed script:

```
txt2dub
```

or from its Python module:

```
python -m txt2dub
```

## Why isn't `txt2dub` an app or web-based service?

`txt2dub` aims to unlock access to the text-to-speech services provided by your operating system, all wrapped in a simple application that tries to improve the workflow for voiceover script writing. It is built on top of the [Textual](https://textual.textualize.io/) rapid application development framework for text-based UIs. This makes it easy to install and run in [any supported terminal](https://textual.textualize.io/getting_started/#requirements) with Python 3.7 or later.

This project doesn't require a subscription, a new account or payment. It's entirely open source, free to use, and it doesn't share your data or the content you create using it with anyone.

## Is `txt2dub` ready for production use?

It has been used successfully for production work by the project's author in Windows 10. Testing on Mac will proceed in the near future. Linux testing will be community-driven. Please report issues with details about your OS (Windows, Mac, Linux + version) and Python environment (version) if you encounter bugs.
