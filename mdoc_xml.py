#!/usr/bin/env python3
import os
import sys


# Help Messages
def help():
    print("Usage: python mdoc_xml.py <command>")
    print("\nCommands:")
    print(" --help, -h      -- Display help")
    print(" --dir,  -d      -- Specify directory")
    print("\nWill default to current directory unless specified.")


# Find MDOC files and add to list
def get_mdocs(directory):
    mdocs = []
    with os.scandir(directory) as entries:
        for entry in entries:
            if entry.is_file() and entry.name.endswith(".mdoc"):
                mdocs.append(entry.name)
    print("Found", len(mdocs), "mdoc files in", str(directory))
    return mdocs


# Extract image shift from MDOC files and store in variables
def extract_image_shift(mdoc):
    image_shift_x = ""
    image_shift_y = ""
    with open(mdoc, 'r') as file:
        for line in file:
            if "ImageShift" in line:
                image_shift = line.strip()
                image_shift_x = (str(image_shift.rsplit()[2]))
                image_shift_y = (str(image_shift.rsplit()[3]))
                return(image_shift_x, image_shift_y)
                break

def write_xml(mdoc):
    is_x, is_y = extract_image_shift(mdoc)
    print(str(mdoc), "has image shift of", is_x, is_y)
    xml_name = mdoc.rsplit(".mdoc",2)[0]
    xml_file = open((str(xml_name) + ".xml"),"w")
    xml_contents = """<MicroscopeImage xmlns="http://schemas.datacontract.org/2004/07/Fei.SharedObjects" xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
    <microscopeData>
        <optics>
            <BeamShift xmlns:a="http://schemas.datacontract.org/2004/07/Fei.Types">
                <a:_x>%s</a:_x>
                <a:_y>%s</a:_y>
            </BeamShift>
        </optics>
    </microscopeData>
</MicroscopeImage>
""" % (is_x, is_y)
    xml_file.writelines(xml_contents)
    xml_file.close()
    return

# Main program execution
def main():

    # Parse command line arguments
    if len(sys.argv) > 1:
        arg1 = sys.argv[1]

        if arg1 == "--help" or arg1 == "-h":
            help()
            sys.exit(0)
        elif arg1 == "--dir" or arg1 =="-d":
            arg2 = sys.argv[2]
            directory = sys.argv[2]
    else:
        directory = "."

    # Run program
    mdoc_files = get_mdocs(directory)
    for i in range (len(mdoc_files)):
        write_xml(mdoc_files[i])

if __name__ == "__main__":
    main()
