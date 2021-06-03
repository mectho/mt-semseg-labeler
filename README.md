# MT Semseg Labeler

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [How to use](#usage)

## About <a name = "about"></a>

MT Semseg Labeler is an annotation application which can be used to label images for semantic segmentation, It can generate the mask labeling file.


## Getting Started <a name = "getting_started"></a>

### Prerequisites

- python3
- tk >= v3.6.9
- Pillow >= v5.1.0


### Installing

- [Download the latest release of this program from the release page.](https://github.com/Mectho/mt-semseg-labeler/releases)
- Launch mt_semseg_labeler.py


## How to use <a name = "usage"></a>

The images must be placed within a folder along with a json file, named classes.json, where the user must indicate the different classes and the related mask pixel values.

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

The outcome of the labeling is a new 8-bit unsigned image with the same dimensions of the original image, of which the pixel values correspond to the selected  classes (the specific values are defined in the file classes.json).

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
