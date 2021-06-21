import json

# All lower-case; we'll convert category names to lower-case when comparing
species_of_interest = ['red_squirrel', 'common_opossum', 'bird_spec', 'white_tailed_deer, red_fox', 'bird',
                       'eastern gray squirrel', 'eastern chipmunk', 'woodchuck', 'wild turkey', 'eastern cottontail',
                       'human', 'vehicle', 'striped skunk', 'northern raccoon', 'horse', 'dog', 'american crow',
                       'coyote', 'bobcat', 'american black bear', 'domestic cat', 'grey fox', 'rabbit', 'car', 'fox']

with open(r'G:\Ketan\Downloads\lila_downloads_by_species\missouri_camera_traps_set1.json') as file:
    missouri = json.load(file)

images_of_interest = []

for image in missouri['images']:
    for species in species_of_interest:
        if species in image['file_name'].lower() and 'Collared_Peccary' not in image['file_name']:
            images_of_interest.append(image)

annotations = []
for a in missouri['annotations']:
    try:
        if any(a['image_id'] in im['id'] for im in images_of_interest):
            annotations.append(a)
    except KeyError:
        pass

images_of_interest = [im for im in images_of_interest if any(im['id'] == a['image_id'] for a in annotations)]
print(len(images_of_interest), len(annotations))

for idx, _ in enumerate(annotations):
    if images_of_interest[idx]['id'] != annotations[idx]['image_id']:
        images_of_interest.remove(images_of_interest[idx])

print(len(images_of_interest), len(annotations))
