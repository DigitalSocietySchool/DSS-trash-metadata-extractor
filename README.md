# DSS Trash MetaData Extractor

Easy tool to extract metadata from images (GPS coord, RCNN bounding boxes).

This project is part of a SummerSchool at the [Digital School Society](https://digitalsocietyschool.org/).
## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
- Python 3
- Pip 3
```

### Installing

A step by step series of examples that tell you how to get a development env running

Say what the step will be to clone the repository:

```bash
$: git clone git@github.com:lucasgrelaud/DSS-trash-metadata-extractor.git
$: cd DSS-trash-metadata-extractor
```

Install the dependencies:

```bash
$: pip3 install -r requirements.txt
```

## Usage

```bash
usage: metadata-extractor.py [-h] [-p] [-j] [--version]
                             bounding-boxes-json output-csv images-dir

positional arguments:
  bounding-boxes-json  JSON file witch contains the bounding boxes of the
                       images The images must be the same as the ones passed
                       as argument (or dir).
  output-csv           Name (with or without path) of the resulting file. The
                       content is formatted as a CSV document.
  images-dir           The path of a directory filed by images to process with
                       the metadata extractor

optional arguments:
  -h, --help           show this help message and exit
  -p, --png            Tell the script to search for PNG images.
  -j, --jpeg           Tell the script to search for JPEG images.
  --version            show program's version number and exit
```

## Extract bounding boxes from Jupiter NoteBook
This tool is made to work with the data retrieved from the [World Cleanup AI](https://github.com/letsdoitworld/wcd-ai)
project.

But we have to modify slightly the Jupyter NoteBook in order to export the bounding boxes of the processed images.

__I. Add the "json" library to the project__
in the "In[1]" section (Mask R-CNN - Visualize Trash detection) add the following line:
```python
import json
```
__II. Replace the code of the image processing__
In the "In[10]" section (Run detection on images) replace all the code by the one bellow:
```python
bounding_boxes = dict()

for image in jpg:
    print(image)
    image_name = image.split("/")[-1]
    image = skimage.io.imread('{}'.format(image))

    # Run object detection
    results = model.detect([image], verbose=1)

    # Display results
    ax = get_ax(1)
    r = results[0]
    bounding_boxes[image_name] = r['rois'].tolist()
    
    visualize.display_instances(image, r['rois'], r['masks'], r['class_ids'], 
                                dataset.class_names, r['scores'], ax=ax,
                                title="Predictions")

print(bounding_boxes)

with open("bounding_boxes.json", 'w') as outfile:
    outfile.write(json.dumps(bounding_boxes))
```

#### III. Process your images
Replace the images in the directory `wcd-ai/Trash_Detection/images` by the ones you want to process and press the button __"restart the kernel, then re-run the whole notebook (with dialog)"__.

Copy the file ``wcd-ai/Trash_Detection/bounding_boxes.json`` where you want. It is the file to use with the metadata extractor.
## Version

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/lucasgrelaud/DSS-trash-metadata-extractor/tags). 

## Authors

* **Lucas GRELAUD** - *Initial work* - [GitHub](https://github.com/lucasgrelaud)


## License

This project is licensed under the GNU GPLv3 License - see the [LICENSE](LICENSE) file for details


