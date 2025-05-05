# PotDict

PotDict is a addon dictionary application for PotPlayer.



## Requirements:

PotDict works pretty well on Windows64, but I haven't tested it on any other platforms.

If you want to run the source code, the following libraries will be required:

-  `readmdict`
- `pyinstaller`

## Installation:

> There's no release yet, so please ignore the following part.

Download the zip file and extract the content to whatever place you feel like. Then run PotDict.exe. I recommend can create a desktop shortcut.



## Usage:

### Basic usage:

![Screenshot](E:\Files\programming\python\PotDict\readme_files\img1.png)

1. Exit PotDict
2. Restart listener
3. Start/Stop listener

Copy `127.0.0.1:65432` or other url displayed and paste it into your browser. 

If you saw something like this, it means PotDict is running:

![](E:\Files\programming\python\PotDict\readme_files\img2.png)

![image-20250505220606455](C:\Users\limuzhi\AppData\Roaming\Typora\typora-user-images\image-20250505220606455.png)

Open PotPlay, open Preferences:

<img src="E:\Files\programming\python\PotDict\readme_files\img3.png"  />

Go to Subtitles > Word Searching:

![](E:\Files\programming\python\PotDict\readme_files\img4.png)

Click "Add" and enter PotDict and `http://127.0.0.1:65432/?q=%%SS`. Remember to replace this url with the actual url you are using:

![](E:\Files\programming\python\PotDict\readme_files\img5.png)

Select PotDict and click "Up" until it's on the top. This way, PotDict will be the default word searching engine for PotPlayer:

![](E:\Files\programming\python\PotDict\readme_files\img6.png)

After saving you changes, click a word in the subtitle. If you see a page like this, PotDict is working properly:

![](E:\Files\programming\python\PotDict\readme_files\img7.png)

### Known Errors & Solutions:

- **If you saw a blank page when searching from PotPlayer, try to set the "Browser" option to "System Default" rather than "Internet Explorer". (Why are people still using IE in 2025?)**

- If the searching page is loading for a very long time, press Ctrl+F5 to refresh. If it's still not working, try to restart the listener.

    If you want to report a BUG or give me a recommendation, please create an Issue on the [GitHub Repository](https://github.com/askformeal/PotDict) or send an E-mail to `zeus1014_2023@163.com`. I'll be most grateful for your feedback. 
