import os
from os.path import join
from os import listdir, rmdir, mkdir
import shutil
from shutil import move, rmtree
import splitfolders

def remove_nested_folders(root):
    """
    removes the nested inner folder of LCTSC data
    mutates the root folder
    """
    for subdir in os.scandir(root):
        subname = subdir.name
        if "LCTSC" in subname:
            for filename in listdir(join(root, subname)):
                move(join(root, subname, filename), join(root, "temp"))
                rmdir(join(root, subname))
                move(join(root, "temp"), join(root, subname))


def create_splits(root, train, val):
    """
    root is path to LCTSC folder after removing nested folders
    train + val must equal 1

    creates a new folder "data" with the training and validation splits
    """
    for subdir in os.listdir(root):
        move(join(root, subdir, "images"), join("temp", subdir))    

    splitfolders.ratio("temp", output="data", seed=1337, ratio=(train, val), group_prefix=None)
    rmtree("temp")

def add_metadata(root):
    """
    root is path to LCTSC folder after removing nested folders
    """
    for split in os.listdir("data"):
        for subdir in os.listdir(join("data", split)):
            mkdir(join("data", split, subdir, "images"))
            for file in os.listdir(join("data", split, subdir)):
                move(join("data", split, subdir, file), join("data", split, subdir, "images"))

            mkdir(join("data", split, subdir, "metadata"))
            shutil.copy(join(root, subdir, "metadata", "1-1.dcm"), join("data", split, subdir, "metadata"))


def main():
    # example root
    root = 'manifest-1557326747206 - Copy\LCTSC'

    remove_nested_folders(root)
    create_splits(root, 0.8, 0.2)
    add_metadata(root)
  
if __name__=="__main__":
    main()
