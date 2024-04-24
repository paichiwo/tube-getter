
![](images/tube_getter_logo.png)

![](screenshots/TG_screenshot_1.png)

---
Tube Getter is a Python application that allows you to download videos and audio from YouTube.
It provides a simple user interface built with customtkinter
and uses the pytubefix library for downloading the YouTube content.
---
## **Features**

*   Download video and audio from YouTube.
*   Support for downloading individual videos or entire playlists.
*   Choose the output format (video or audio).
*   Monitor the download progress, including progress, download speed, and completion status.
*   Choose the download folder in the settings window

## **Prerequisites**

*   Python 3.x
*   pytubefix
*   customtkinter
*   pillow
*   darkdetect
*   sv-ttk

## **Installation**

### SOURCE:

Clone the repository:   
`git clone https://github.com/paichiwo/tube-getter.git`

Install the required dependencies:
`pip install -r requirements.txt`

Run the application:   
`python main.py`


### WINDOWS:

Download `tube_getter.exe` from https://github.com/paichiwo/tube-getter/releases/tag/v1.2.8

Run the application. 

Note: Application is portable, no installation required.

Note: Your antivirus software might find this application suspicious. 
This is due to the nature of pyinstaller behavior.
It's a common problem and well acknowledged. 
Exemption might have to be added in windows defender or other antivirus software that you use.
## **Usage**

- Run the application, the window will appear.


- Enter the YouTube video URL or playlist URL in the input field and click "Add" or press Enter, 
you can also add URLs one by one.


- Choose Audio or Video to update the relevant information about the YouTube stream.


- Select the download folder by clicking the "Settings" button and click "Close" button to save the settings.


- The table will display the list of queued video or audio streams.


- Click the "Download" button to start the download process and monitor the download progress in the table. Completed downloads will show the status as “Complete.”

## **Contributing**

_I'm constantly working on this application, this code might change a lot._
_If you find any bugs, please feel free to open an issue._

If you are interested in contributing to the development of the YouTube Downloader,
you are welcome to create a pull request on the project's GitHub repository. 
By contributing to the project, you can help improve the functionality, 
stability, and overall quality of the Tube Getter application, which is much appreciated.

## **License**

This project is licensed under the [MIT License](LICENSE).

## **Acknowledgements**

*   [pytubefix](https://pytubefix.readthedocs.io/en/latest/) - Python library for downloading YouTube videos

## TODO:

- bind enter key with url entry
- bind control-z with url entry
- bind right mouse click on a treeview / implement menu with 'delete' and 'open folder' options
