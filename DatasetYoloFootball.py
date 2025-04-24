import cv2
import os
import glob
import json
import shutil
from pprint import pprint
if __name__ == '__main__':


    root_train = "Dataset/Train_Football"
    root_val = "Dataset/Test_Football"
    output_path = "Checked_Dataset"




    video_train_paths = list(glob.iglob("{}/*/*.mp4".format(root_train)))

    anno_train_paths = list(glob.iglob("{}/*/*.json".format(root_train)))

    video_val_paths = list(glob.iglob("{}/*/*.mp4".format(root_val)))

    anno_val_paths = list(glob.iglob("{}/*/*.json".format(root_val)))

    video_train_wo_ext = [video_train_path.replace(".mp4","") for video_train_path in video_train_paths]

    video_val_wo_ext = [video_val_path.replace(".mp4", "") for video_val_path in video_val_paths]

    anno_train_wo_ext = [anno_train_path.replace(".json", "") for anno_train_path in anno_train_paths]

    anno_val_wo_ext = [anno_val_path.replace(".json", "") for anno_val_path in anno_val_paths]



    paths_train = list(set(video_train_wo_ext) & set(anno_train_wo_ext))

    paths_val = list(set(video_val_wo_ext) & set(anno_val_wo_ext))

    if os.path.isdir(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path)
    os.makedirs(os.path.join(output_path, "images", "train"))
    os.makedirs(os.path.join(output_path, "images", "val"))
    os.makedirs(os.path.join(output_path, "labels", "train"))
    os.makedirs(os.path.join(output_path, "labels", "val"))


    for idx,path_train in enumerate(paths_train):

        video = cv2.VideoCapture("{}.mp4".format(path_train))

        num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        with open("{}.json".format(path_train),"r") as json_file :
            json_data = json.load(json_file)

        if num_frames != len(json_data["images"]):
            print("Something is wrong with the game {}".format(path_train))
            paths_train.remove(path_train)
        width = json_data["images"][0]["width"]
        height = json_data["images"][0]["height"]
        all_objects = [{"image_id": obj["image_id"],"bbox": obj["bbox"],"category_id":obj["category_id"]} for obj in json_data["annotations"] if obj["category_id"] in [3,4]]

        frame_counter = 0
        while video.isOpened():
            flag,frame = video.read()
            if not flag:
                break

            current_objects = [obj for obj in all_objects if obj["image_id"]-1 == frame_counter]

            cv2.imwrite(os.path.join(output_path, "images","train", "{}_{}.jpg".format(idx, frame_counter)), frame)

            with open(os.path.join(output_path, "labels","train", "{}_{}.txt".format(idx, frame_counter)),"w") as f:
                for obj in current_objects:
                    xmin, ymin,w,h = obj["bbox"]
                    xmin /= width
                    w /= width
                    ymin /= height
                    h /= height
                    if obj["category_id"] == 4:
                        category = 0
                    else:
                        category = 1
                    f.write("{} {:06f} {:06f} {:06f} {:06f}\n".format(category,xmin+w/2,ymin+h/2,w,h))
            frame_counter +=1

    for idx,path_val in enumerate(paths_val):

        video = cv2.VideoCapture("{}.mp4".format(path_val))

        num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        with open("{}.json".format(path_val),"r") as json_file :
            json_data = json.load(json_file)

        if num_frames != len(json_data["images"]):
            print("Something is wrong with the game {}".format(path_val))
            paths_val.remove(path_val)
        width = json_data["images"][0]["width"]
        height = json_data["images"][0]["height"]
        all_objects = [{"image_id": obj["image_id"],"bbox": obj["bbox"],"category_id":obj["category_id"]} for obj in json_data["annotations"] if obj["category_id"] in [3,4]]

        frame_counter = 0
        while video.isOpened():
            flag,frame = video.read()
            if not flag:
                break

            current_objects = [obj for obj in all_objects if obj["image_id"]-1 == frame_counter]

            cv2.imwrite(os.path.join(output_path, "images","val", "{}_{}.jpg".format(idx, frame_counter)), frame)

            with open(os.path.join(output_path, "labels","val", "{}_{}.txt".format(idx, frame_counter)),"w") as f:
                for obj in current_objects:
                    xmin, ymin,w,h = obj["bbox"]
                    xmin /= width
                    w /= width
                    ymin /= height
                    h /= height
                    if obj["category_id"] == 4:
                        category = 0
                    else:
                        category = 1
                    f.write("{} {:06f} {:06f} {:06f} {:06f}\n".format(category,xmin+w/2,ymin+h/2,w,h))
            frame_counter +=1