import os
import boto3

from jinja2 import Template

path = "images"

os.chdir(path)

# Instantiates a client
rekogClient = boto3.client('rekognition')

categories = []


# iterate through all images
for root, directories, files in os.walk("."):

    for directory in directories:

        directory_map = {}
        directory_map["name"] = directory
        directory_map["ltks"] = []

        dirpath = "./" + directory

        for img_root, img_dirs, img_files in os.walk(dirpath):
            ltks = []
            for file_name in img_files:
                if file_name.endswith(('.jpg','.webp')):
                    ltk_name = file_name.split(".")[0]
                    ltk_id = ltk_name.split("_")[0]
                    image_id = ltk_name.split("_")[1]
                    ltk_url = "https://www.liketoknow.it/ltk/"+ltk_id
                    image_url = "https://images.liketoknow.it/"+image_id+'?auto=format&fm=webp&w=360&q=80&dpr=1'

                    with open(dirpath + "/" + file_name, 'rb') as image_file:
                        foundFace = False
                        faceList = []
                        content = image_file.read()
                        response = rekogClient.detect_faces(
                            Image={
                                'Bytes':content
                            },
                            Attributes=[
                                'ALL'
                            ]
                        )

                        print('Detecting faces for : '+file_name)

                        faces = response['FaceDetails']
                        if len(faces) != 0:
                            foundFace = True
                            for face in faces:
                                faceDetails = {}
                                faceDetails["confidence"] = round(face['Confidence'], 2)
                                faceDetails["age_range"] = str(face['AgeRange']['Low']) + '-' + str(face['AgeRange']['High'])
                                faceDetails["gender"] = face['Gender']['Value']
                                faceDetails["gender_confidence"] = round(face['Gender']['Confidence'], 2)
                                faceList.append(faceDetails)
                    
                    directory_map["ltks"].append({
                        "name":ltk_name,
                        "url": ltk_url,
                        "image_url": image_url,
                        "face_found": foundFace,
                        "faces": faceList
                    })
    
        categories.append(directory_map)

with open('../template.html') as file_:
    template = Template(file_.read())
rendered_file = template.render(categories=categories)

bytes = rendered_file.encode(encoding='UTF-8')

with open("../results.html", "wb") as f:
    f.write(bytes)

