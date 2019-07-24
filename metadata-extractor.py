#!/usr/bin/env python3
"""
Module Docstring
"""

__author__ = "Lucas GRELAUD <github.com/lucasgrelaud>"
__version__ = "0.1.0"
__license__ = "GNU GPLv3"

import os
import sys
import glob
import argparse
import json
import csv
from PIL import Image
from PIL.ExifTags import GPSTAGS

GPSINFO_TAG = 34853


def extract_gps_exif(images_path_list: list) -> dict:
    images_data_dict: dict = dict()
    for image in images_path_list:
        image_fd: Image = Image.open(image)
        image_name = image.split("/")[-1]
        image_data: dict = dict()
        if image_fd:
            image_exif_gps = image_fd._getexif().get(GPSINFO_TAG)
            if image_exif_gps:
                for entry in image_exif_gps:
                    tag = GPSTAGS.get(entry)
                    image_data[tag] = image_exif_gps.get(entry)
                images_data_dict[image_name] = {'GPS_raw': image_data}
        image_fd.close()

    return images_data_dict


def get_float(degrees_minutes_seconds: tuple) -> float:
    return float(degrees_minutes_seconds[0]) / float(degrees_minutes_seconds[1])


def to_decimal_degrees(degrees_minutes_seconds: tuple) -> float:
    if type(degrees_minutes_seconds[0]) != int:
        degrees = get_float(degrees_minutes_seconds[0])
    else:
        degrees = float(degrees_minutes_seconds[0])
    if type(degrees_minutes_seconds[1]) != int:
        minutes = get_float(degrees_minutes_seconds[1])
    else:
        minutes = float(degrees_minutes_seconds[1])
    if type(degrees_minutes_seconds[2]) != int:
        seconds = get_float(degrees_minutes_seconds[2])
    else:
        seconds = float(degrees_minutes_seconds[2])

    return degrees + (minutes / 60.0) + (seconds / 3600.0)


def convert_coordinates(images_data_dict) -> None:
    latitude: float = None
    longitude: float = None
    altitude: float = None

    for image in images_data_dict:
        try:
            gps_latitude: tuple = images_data_dict[image]["GPS_raw"]["GPSLatitude"]
            gps_latitude_ref: str = images_data_dict[image]["GPS_raw"]["GPSLatitudeRef"]
            gps_longitude: tuple = images_data_dict[image]["GPS_raw"]["GPSLongitude"]
            gps_longitude_ref: str = images_data_dict[image]["GPS_raw"]["GPSLongitudeRef"]
            gps_altitude: tuple = images_data_dict[image]["GPS_raw"]["GPSAltitude"]
            gps_altitude_ref: str = images_data_dict[image]["GPS_raw"]["GPSAltitudeRef"]

            latitude = to_decimal_degrees(gps_latitude)
            if gps_latitude_ref != "N":
                latitude = 0 - latitude

            longitude = to_decimal_degrees(gps_longitude)
            if gps_longitude_ref != "E":
                longitude = 0 - longitude

            altitude = get_float(gps_altitude)
            if gps_altitude_ref != 0:
                altitude = 0 - altitude

            images_data_dict[image]["GPS"] = {"Altitude": altitude, "Longitude": longitude, "Latitude": latitude}

        except KeyError:
            print("Cannot convert the GPS coordinates of " + image)


def merge_images_data(images_data_dict: dict, bounding_boxes: dict) -> None:
    for image in images_data_dict:
        boxes: list = bounding_boxes.get(image)
        if boxes:
            images_data_dict[image]["Bounding_Boxes"] = boxes

def generate_csv(images_data_dict: dict, csv_file_fp: object):
    csv_writer = csv.writer(csv_file_fp, dialect='excel')

    # Write the header of the csv file
    csv_writer.writerow(['Image name', 'Shape ID', 'Bounding Boxes', "Longitude", "Latitude", "Altitude"])

    # Process each images
    for image in images_data_dict:
        boxes: list = images_data_dict[image].get("Bounding_Boxes")
        if boxes is None:
            if images_data_dict[image].get("GPS"):
                csv_writer.writerow([image, 0, "",
                                     images_data_dict[image]["GPS"].get("Longitude", ""),
                                     images_data_dict[image]["GPS"].get("Latitude", ""),
                                     images_data_dict[image]["GPS"].get("Altitude", "")
                                     ])
            else:
                csv_writer.writerow([image,0, "", "", "", ""])
        else:
            box_id = 1
            if images_data_dict[image].get("GPS"):
                for box in boxes:
                    csv_writer.writerow([image, box_id, box,
                                         images_data_dict[image]["GPS"].get("Longitude", ""),
                                         images_data_dict[image]["GPS"].get("Latitude", ""),
                                         images_data_dict[image]["GPS"].get("Altitude", "")
                                         ])
                    box_id += 1
            else:
                for box in boxes:
                    csv_writer.writerow([image, box_id, box, "", "", ""])

def main(args):
    images_path_list: list = list()

    # List the desired pictures
    if args['png']:
        png: list = glob.glob(args['images-dir'] + "*.png")
        images_path_list.extend(png)
    if args['jpeg']:
        jpg: list = glob.glob(args['images-dir'] + "*.jpg")
        jpeg: list = glob.glob(args['images-dir'] + "*.jpeg")
        images_path_list.extend(jpg)
        images_path_list.extend(jpeg)

    if len(images_path_list) == 0:
        print("The program as loaded no images, please check the arguments you have given.", file=sys.stderr)
        print(images_path_list, file=sys.stderr)
        exit(1)

    # Create the data dictionary for the images
    images_data_dict: dict

    # Get the GeoTag from the pictures
    images_data_dict = extract_gps_exif(images_path_list)

    # Convert the raw GPS data to decimal degree ones
    convert_coordinates(images_data_dict)

    # Get the bounding boxes from the JSON dump
    bounding_boxes_dict: dict = json.load(args["bounding-boxes-json"])
    merge_images_data(images_data_dict, bounding_boxes_dict)

    # Generate the resulting csv file
    generate_csv(images_data_dict, args.get('output-csv'))


if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("bounding-boxes-json", type=argparse.FileType('r', encoding='UTF-8'),
                        help="JSON file witch contains the bounding boxes of the images\n"
                             "The images must be the same as the ones passed as argument (or dir).")
    parser.add_argument("output-csv", type=argparse.FileType('w', encoding='UTF-8'),
                        help="Name (with or without path) of the resulting file.\n"
                             "The content is formatted as a CSV document.")
    parser.add_argument("images-dir",
                        help="The path of a directory filed by images to process with the metadata extractor")

    # Optional argument to fetch couple types of pictures.
    # The argument '--images-dir' is required
    parser.add_argument("-p", "--png", action="store_true", default=False,
                        help="Tell the script to search for PNG images.")
    parser.add_argument("-j", "--jpeg", action="store_true", default=False,
                        help="Tell the script to search for JPEG images.")

    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = vars(parser.parse_args())

    if args['images-dir'][:2] == "~/":
        args['images-dir'] = os.path.expanduser(args['images-dir'])
    if args['images-dir'][-1] != os.path.sep or args['images-dir'][-1] != os.path.altsep:
        args['images-dir'] += os.path.sep
    main(args)
