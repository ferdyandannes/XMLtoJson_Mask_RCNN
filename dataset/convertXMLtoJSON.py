"""
converterXMLtoJSON

converts
detect all annotations in xml file
it works for one class in mask rcnn - damage class

@author Adonis Gonzalez

"""

import xml.etree.cElementTree as ET
import json
import os
import os.path as path

#################################################
#####                PATHS                  #####
#################################################
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
path = []#list used for two folder /train and /val
train = os.path.join(ROOT_DIR, "train")
val = os.path.join(ROOT_DIR, "val")
path = [train, val]
count = 0

def process_bar(count, total, status=''):
    bar_len = 50
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    print(('[%s] %s%s ...%s\r' % (bar, percents, '%', status)))


def grabNamesImages():
    for file in path:
        files = os.listdir(file)
        for name in files:
            #imgs = []
            with open(file + '/image.txt', 'w') as f:
                for item in files:
                    if (item.endswith('.jpg')):
                        f.write("%s\n" % item)
            f.close()
        print("List of images, images.tx, was save in", file)


def XMLtoJson():
    for dir in path:
        images, bndbox, size, polygon, all_json = {}, {}, {}, {}, {}

        imgs_list = open(dir+'/image.txt','r').readlines()

        count = 1
        total = len(imgs_list)

        for img in imgs_list: #for each image in the list in image.txt
            process_bar(count, total)
            count += 1
            if 'jpg' in img:
                img_name = img.strip().split('/')[-1]
                namexml = (img_name.split('.jpg')[0])

                images.update({"filename": img_name})
                xml_n = namexml + '.xml'

                tree = ET.ElementTree(file=dir+'/'+xml_n)
                root = tree.getroot()

                #more dics for create json documents
                counterObject,xmin,xmax,ymin,ymax,regionsTemp,regi = {},{},{},{},{},{},{}

                number = 0
                for child_of_root in root:
                    if child_of_root.tag == 'filename':
                        image_id = (child_of_root.text)
                        sizetmp = os.path.getsize(dir+'/'+image_id)

                    if child_of_root.tag == 'object':
                        for child_of_object in child_of_root:
                            if child_of_object.tag == 'name':
                                category_id = child_of_object.text
                                counterObject[category_id] = number

                            if child_of_object.tag == 'bndbox':
                                for child_of_root in child_of_object:
                                    if child_of_root.tag == 'xmin':
                                        xmin[category_id] = int(child_of_root.text)

                                    if child_of_root.tag == 'xmax':
                                        xmax[category_id] = int(child_of_root.text)

                                    if child_of_root.tag == 'ymin':
                                        ymin[category_id] = int(child_of_root.text)

                                    if child_of_root.tag == 'ymax':
                                        ymax[category_id] = int(child_of_root.text)

                        xmintmp = int(xmax[category_id] - xmin[category_id]) / 2
                        xvalue = int(xmin[category_id] + xmintmp)

                        ymintemp = int(ymax[category_id] - ymin[category_id]) / 2
                        yvalue = int(ymin[category_id] + ymintemp)

                        regions, regions1 = {} , {}
                        regionsTemp = ({"all_points_x": (xmin[category_id], xvalue, xmax[category_id], xmax[category_id], xmax[category_id], xvalue, xmin[category_id], xmin[category_id], xmin[category_id]),
                                        "all_points_y": (ymin[category_id], ymin[category_id], ymin[category_id], yvalue, ymax[category_id], ymax[category_id], ymax[category_id], yvalue, ymin[category_id])})

                        damage = {"damage": "damage"}
                        regions.update({"region_attributes": damage})

                        shapes = {"shape_attributes": regionsTemp}

                        regions.update(shapes)

                        polygon.update({"name": "polygon"})
                        regions.update(shapes)
                        regions.update(polygon)

                        regi[number] = regions.copy()
                        #print(regi[number],[category_id])

                        regions = {"regions": regi}

                        images.update(regions)
                        size = {"size": sizetmp}
                        images.update(size)

                        all_json[img_name] = images.copy()

                        number = number + 1
        #print(all_json)
        with open(dir+'/'+"dataset.json", "a") as outfile:
            json.dump(all_json, outfile)
            print("File dataset.json was save in: ",dir)
            #open(dir+'/'+"dataset.json", "w").close()


if __name__ == "__main__":

    #check if alreday exist dataset.json file in /train and /val

    fileindirTrain = (train+"/dataset.json")
    fileindirVal = (val+"/dataset.json")

    if os.path.isfile(fileindirTrain):
        os.remove(fileindirTrain)
        print("deleting an existent file --> dataset.json from /train")

    if os.path.isfile(fileindirVal):
        os.remove(fileindirVal)
        print("deleting an existent file --> dataset.json from /val")

    grabNamesImages()
    XMLtoJson()





