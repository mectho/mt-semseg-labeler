# Mt Semseg Labeler

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [How to use](#usage)

## About <a name = "about"></a>

Mt Semseg Labeler is an image(s) labeling/annotation application which allows the user to label his images, It can generate the mask labeling file for semantic segmentation.

Write about 1-2 paragraphs describing the purpose of your project.

## Getting Started <a name = "getting_started"></a>

### Prerequisites

- python3
- tk >= v3.6.9
- Pillow >= v5.1.0


### Installing

- [Download the latest release of this program from the release page.](https://github.com/Mectho/mt-semseg-labeler/releases)
- Open the directory
- Launch mt_semseg_labeler.py

The classes.json file contains ...

in the example, the content of classes.json is:
```json
{
"orange":10,
"banana":15,
"apple":20,
"pear":25,
"kiwi":30,
"coconut":35,
"medlar":40,
"mango":45
}
```
## How to use <a name = "usage"></a>

#### First Steps
1| Launch the program 

<img width="640" height="360" src="gitImages/ms-semseg 1.png"/>
2| Click On File->Open Folder 

<img width="640" height="360" src="gitImages/ms-semseg 2.png"/>
3| Open the "data" folder 

<img width="640" height="360" src="gitImages/ms-semseg 3.png"/>
4| Click On "Ok" button

<img width="640" height="360" src="gitImages/ms-semseg 4.png"/>

#### Hotkeys

| Command | Description |
| --- | --- |
| Scroll wheel       | Increase/Decrease zoom                     |
| Left Click         | Move Over the image                        |
| Ctrl + Left Click  | Draw on the mask                           |
| Ctrl + Right Click | Erase the mask                             |
| Ctrl + "+"/"-"     | Increase/Decrease the drawing area         | 
| Ctrl + "."         | Change the drawing area shape              |


## License

Code released under the MIT License.
