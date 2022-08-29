import shutil
from xml.dom import minidom
import json
import os
import argparse

from util import listdir_fullpath, flatten_nan, glob_re, dir_path, find_file

sa_classId = {
    "ILM": 1,
    "RNFL": 2,
    "GCL": 3,
    "IPL": 4,
    "INL": 5,
    "OPL": 6,
    "ELM": 7,
    "PR1": 8,
    "PR2": 9,
    "RPE": 10,
    "BM": 11,
    "FLUID": 12
}


def parse_annot_xml(path):
    dom = minidom.parse(path)
    ls = dom.getElementsByTagName('LayerSegmentation')
    assert len(ls) == 1, "Layer Segmentation should be provided and unique"

    slice_annotations = {}
    for node in ls[0].childNodes:
        if node.nodeType == node.TEXT_NODE:  # ignore text nodes
            continue

        assert len(node.childNodes) == 1, f"{node.tagName} should have only 1 data node"
        data = node.firstChild.data
        assert type(data) == str
        parsed_data = [(x, float(y)) for x, y in enumerate(data.split(" ")[:-1]) if y != 'nan']
        if len(parsed_data) > 2:
            slice_annotations[node.tagName] = parsed_data

    return slice_annotations


def convert_to_sa(vol_annotations):
    sa_annotations = {"___sa_version___": "1.0.0"}
    for slice_name, slice_annotations in vol_annotations.items():
        # Initialize slice
        sa_annotations[slice_name] = {"instances": [],
                                      "tags": [],
                                      "metadata": {"version": "1.0.0",
                                                   "name": slice_name,
                                                   "status": "In progress"
                                                   }
                                      }

        # Append all annotation instances
        for layer_name, data in slice_annotations.items():
            annot_instance = {"type": "polyline",
                              "classId": sa_classId[layer_name],
                              "probability": 100,
                              "points": flatten_nan(data),
                              "groupId": 0,
                              "pointLabels": {},
                              "locked": False,
                              "visible": True,
                              "attributes": []
                              }

            sa_annotations[slice_name]["instances"].append(annot_instance)

    return sa_annotations


def main():
    parser = argparse.ArgumentParser(description='Compile Heidelberg Layer Segmentation labels to SuperAnnotate')
    parser.add_argument('--path', type=dir_path, help='Path to SuperAnnotate directory', required=True)
    args = parser.parse_args()

    # Accumulate Heidelberg's layer segmentations
    vol_annotations = {}
    for bscan_path in glob_re(r'.*bscan_\d+.tiff', listdir_fullpath(args.path)):
        annot_path = bscan_path.replace('bscan', 'segmentation').replace('tiff', 'xml')
        bscan_name = os.path.basename(bscan_path)
        vol_annotations[bscan_name] = parse_annot_xml(annot_path)
        print(f'Parsed Heidelberg annotations from {annot_path}')

    # Convert to SuperAnnotate format
    sa_annotations = convert_to_sa(vol_annotations)

    # Dump to JSON
    output_file_path = find_file('annotations.json', args.path)
    with open(output_file_path, 'w+') as file:
        json.dump(sa_annotations, file, separators=(',', ':'))
        print(f'Dumped SuperAnnotate annotations to {output_file_path}')

    # Copy classes & config
    for file_to_copy in ['classes.json', 'config.json']:
        dest = find_file(file_to_copy, args.path)
        shutil.copy2(file_to_copy, dest)
        print(f'Copied {file_to_copy} to {dest}')

    print('Done.')


if __name__ == '__main__':
    main()
