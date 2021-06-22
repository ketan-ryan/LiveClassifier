from tqdm import tqdm
import json
import glob
import os

# All lower-case; we'll convert category names to lower-case when comparing
species_of_interest = ['red_squirrel', 'common_opossum', 'bird_spec', 'white_tailed_deer, red_fox', 'bird',
                       'eastern gray squirrel', 'eastern chipmunk', 'woodchuck', 'wild turkey', 'eastern cottontail',
                       'human', 'vehicle', 'striped skunk', 'northern raccoon', 'horse', 'dog', 'american crow',
                       'coyote', 'bobcat', 'american black bear', 'domestic cat', 'grey fox', 'rabbit', 'car', 'fox']

images_of_interest = []
list_indices = []
annotations_of_interest = []

# read_files = glob.glob(r"G:/Ketan/Downloads/lila_downloads_by_species/caltech*.json")
# with open(r"G:/Ketan/Downloads/lila_downloads_by_species/merged_file.json", "w") as outfile:
#     outfile.write('[{}]'.format(
#         ','.join([open(f, "r").read() for f in read_files])))
#
# exit(0)

with open(r'G:/Ketan/Downloads/lila_downloads_by_species/caltech_bboxes_20200316.json', 'r') as fp:
    data = json.load(fp)

    annotations = data['annotations']
    images = data['images']

    annotations = sorted(annotations, key=lambda a: a['image_id'])
    images = sorted(images, key=lambda i: i['id'])

    with open('G:/Ketan/Downloads/lila_downloads_by_species/test-caltech-sorted.json', 'w') as out:
        json.dump(annotations, out, indent=3)
        json.dump(images, out, indent=3)

for file_name in [file for file in os.listdir(r'G:/Ketan/Downloads/lila_downloads_by_species/') if
                  file.endswith('.json')]:
    print(file_name)
    with open(r'G:/Ketan/Downloads/lila_downloads_by_species/' + file_name) as json_file:
        data = json.load(json_file)

        annotations = data['annotations']
        images = data['images']

        annotations = sorted(annotations, key=lambda a: a['image_id'])
        images = sorted(images, key=lambda i: i['id'])

        # print(len(images), len(annotations))
        for idx, image in enumerate(tqdm(images)):
            ann = annotations[idx]
            if image['id'] == ann['image_id']:
                try:
                    if ann['sequence_level_annotation'] is False and ann['bbox']:
                        for i_s, species in enumerate(species_of_interest):
                            if species in image['file_name'].lower() and 'Collared_Peccary' not in image['file_name']:
                                images_of_interest.append(image)
                                annotations_of_interest.append(ann)
                                list_indices.append(i_s)
                except KeyError:
                    continue
    print(len(images_of_interest), len(list_indices), len(annotations_of_interest))

print(len(images_of_interest), len(list_indices), len(annotations_of_interest))

# Now we have matching lists of images, annotations, and classes: convert to YOLO format
for idx, _ in enumerate(annotations_of_interest):
    box = annotations_of_interest[idx]['bbox']
    xmin, ymin, width, height = box[0], box[1], box[2], box[3]
    x_center = (xmin + width) / 2
    y_center = (ymin + height) / 2
    normal_x_center = x_center / images_of_interest[idx]['width']
    normal_width = width / images_of_interest[idx]['width']
    normal_y_center = y_center / images_of_interest[idx]['height']
    normal_height = height / images_of_interest[idx]['height']

    class_id = list_indices[idx]

    string = f"{class_id} {normal_x_center} {normal_y_center} {normal_width} {normal_height}"
    image_id = images_of_interest[idx]['id']

    # create file for r/w, overwrite if exists
    with open(f'yolo_labels/{image_id}.txt', 'w+') as file:
        file.write(string)
