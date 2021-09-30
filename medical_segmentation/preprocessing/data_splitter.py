import os
from os.path import join
import shutil

import click
import splitfolders

def remove_nested_folders(root):
    """
    removes the nested inner folder of LCTSC data
    mutates the root folder
    """
    for subdir in os.scandir(root):
        subname = subdir.name
        if "LCTSC" in subname:
            for filename in os.listdir(join(root, subname)):
                shutil.move(join(root, subname, filename), join(root, "temp"))
                os.rmdir(join(root, subname))
                shutil.move(join(root, "temp"), join(root, subname))


def create_splits(root, train, val):
    """
    root is path to LCTSC folder after removing nested folders
    train + val must equal 1

    creates a new folder "data" with the training and validation splits
    """
    for subdir in os.listdir(root):
        shutil.move(join(root, subdir, "images"), join("temp", subdir))

    splitfolders.ratio("temp", output="data", seed=1337, ratio=(train, val), group_prefix=None)
    shutil.rmtree("temp")

def add_metadata(root):
    """
    root is path to LCTSC folder after removing nested folders
    """
    for split in os.listdir("data"):
        for subdir in os.listdir(join("data", split)):
            os.mkdir(join("data", split, subdir, "images"))
            for file in os.listdir(join("data", split, subdir)):
                shutil.move(
                    join("data", split, subdir, file),
                    join("data", split, subdir, "images")
                )

            os.mkdir(join("data", split, subdir, "metadata"))
            shutil.copy(
                join(root, subdir, "metadata", "1-1.dcm"),
                join("data", split, subdir, "metadata")
            )

@click.command()
@click.option('--root-dir', help='Root directory for RTSTRUCT files')
def main(root_dir):
    remove_nested_folders(root_dir)
    create_splits(root_dir, 0.8, 0.2)
    add_metadata(root_dir)

if __name__=="__main__":
    main()
