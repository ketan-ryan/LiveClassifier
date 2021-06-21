import json

# All lower-case; we'll convert category names to lower-case when comparing
species_of_interest = ['red_squirrel', 'common_opossum', 'bird_spec', 'white_tailed_deer, red_fox', 'bird',
                       'eastern gray squirrel', 'eastern chipmunk', 'woodchuck', 'wild turkey', 'eastern cottontail',
                       'human', 'vehicle', 'striped skunk', 'northern raccoon', 'horse', 'dog', 'american crow',
                       'coyote', 'bobcat', 'american black bear', 'domestic cat', 'grey fox', 'rabbit', 'car', 'fox']

with open('missouri_camera_traps_set1.json') as file:
    missouri = json.load(file)

images_of_interest = []
list_indices = []

# Load images and annotations into lists, keeping track of what class the image is
for image in missouri['images']:
    for species in species_of_interest:
        if species in image['file_name'].lower() and 'Collared_Peccary' not in image['file_name']:
            images_of_interest.append(image)

# Load annotations, matching ids and if they have a bounding box associated
annotations = []
for a in missouri['annotations']:
    try:
        if any(a['image_id'] in im['id'] for im in images_of_interest) and a['bbox']:
            annotations.append(a)
    except KeyError:
        pass

# Trim list of images to those with bounding boxes
images_of_interest = [im for im in images_of_interest if any(im['id'] == a['image_id'] for a in annotations)]
print(len(images_of_interest), len(annotations))

for idx, _ in enumerate(annotations):
    if images_of_interest[idx]['id'] != annotations[idx]['image_id']:
        images_of_interest.remove(images_of_interest[idx])

# Trim list of classes
for image in images_of_interest:
    for idx, species in enumerate(species_of_interest):
        if species in image['file_name'].lower() and 'Collared_Peccary' not in image['file_name']:
            list_indices.append(idx)
            break

# Now we have matching lists of images, annotations, and classes: convert to YOLO format
for idx, _ in enumerate(annotations):
    box = annotations[idx]['bbox']
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
