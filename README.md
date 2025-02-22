This Python application is intended for use on a mac. 

Users are given 4 options:

1. Select a folder containing files to be tagged
It will ask you to select a folder that contains PDF documents, text (.txt) documents or video files (.mp4, .mkv or .webm) to which you would like to automatically add tags. 

The tags will be generated by KeyBERT and added both to the file's own metadata as well as Finder tags.
You can read the tags in the file's own metadata by using a good PDF viewer and visiting the properties of the document or, in the case of a video file, by using a media file inspector such as Invisor.
As for the Finder tags, they can simply be viewed by selecting the file and pressing CMD + I.

2. Sync the tags that have already been defined in the Finder to the file's metadata
Finder tags can easily be modified using the app Tagception. However, please note that the Finder doesn't support nested tags.

3. Open a graph in your default browser to view the files and their associated tags
4. Quit the app

Save the app to your Home folder (~) for easy access:

```
cd
git clone https://github.com/odebroqueville/tagify.git
```

To use this app, you will need to have Python 3.11 installed along with several Python packages.

I recommend first installing miniconda using Homebrew:

`brew install --cask miniconda`

Once miniconda has been installed, you'll need to initialize conda for your zsh shell:

`conda init zsh`

This will modify your ~/.zshrc file to set up the conda environment.

You can now either restart your terminal or to apply the changes immediately run:

`source ~/.zshrc`

You can now create an environment for Python 3.11 which we will call py311:

`conda create -n py311 python=3.11`

To activate the  environment:

`conda activate py311`

Next, we will install the required Python packages:

`pip install openai-whisper inflect pymupdf keybert torch 'numpy<2' pyvis pillow`

Finally, we will need to install ffmpeg and tag (from https://github.com/jdberry/tag) using Homebrew:

`brew install ffmpeg tag`

We should now be ready to run the app:

`python ~/tagigy/main.py`

As a final word, I strongly recommend viewing all your tags with Tagception (from https://madebyevan.com/tagception/).
