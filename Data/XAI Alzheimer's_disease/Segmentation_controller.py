import numpy as np
import cv2
import nibabel as nib
from utility import *

class Segmentation_controller():

    def __init__(self, search_dir="/"):
        self.search_dir = search_dir

        self.drop_list = [5, 26, 29, 30, 44, 58, 62, 72, 77, 85, 80,]
        # Not 5, 26, 30, 44, 58, 62, 77, 85

        self.labeled_dict = {0: "Background", 2: "Left-Cerebral-WM", 3: "Left-Cerebral-Cortex", 4: "Left-Lateral-Ventricle",
                    7: "Left-Cerebellum-WM", 8: "Left-Cerebellum-Cortex", 10: "Left-Thalamus", 11: "Left-Caudate", 12: "Left-Putamen",
                    13: "Left-Pallidum", 14: "3rd-Ventricle", 15: "4th-Ventricle", 16: "Brain-Stem", 17: "Left-Hippocampus",
                    18: "Left-Amygdala", 24: "CSF", 28: "Left-VentralDC", 31: "Left-choroid-plexus", 41: "Right-Cerebral-WM",
                    42: "Right-Cerebral-Cortex", 43: "Right-Lateral-Ventricle", 46: "Right-Cerebellum-WM", 47: "Right-Cerebellum-Cortex",
                    49: "Right-Thalamus-Proper", 50: "Right-Caudate", 51: "Right-Putamen", 52: "Right-Pallidum", 53: "Right-Hippocampus",
                    54: "Right-Amygdala", 60: "Right-VentralDC", 63: "Right-choroid-plexus"
                    }

        self.labeled_dict_reverse = {"Background" : 0, "Left-Cerebral-WM" : 2, "Left-Cerebral-Cortex" : 3,"Left-Lateral-Ventricle" : 4,
                    "Left-Cerebellum-WM" : 7, "Left-Cerebellum-Cortex" : 8, "Left-Thalamus" : 10, "Left-Caudate" : 11, "Left-Putamen" : 12,
                    "Left-Pallidum" : 13, "3rd-Ventricle" : 14, "4th-Ventricle" : 15, "Brain-Stem" : 16, "Left-Hippocampus" : 17,
                    "Left-Amygdala" : 18, "CSF" : 24, "Left-VentralDC" : 28, "Left-choroid-plexus" : 31, "Right-Cerebral-WM" : 41,
                    "Right-Cerebral-Cortex" : 42, "Right-Lateral-Ventricle" : 43, "Right-Cerebellum-WM" : 46, "Right-Cerebellum-Cortex" : 47,
                    "Right-Thalamus-Proper" : 49, "Right-Caudate" : 50, "Right-Putamen" : 51, "Right-Pallidum" : 52, "Right-Hippocampus" : 53,
                    "Right-Amygdala" : 54, "Right-VentralDC" : 60, "Right-choroid-plexus":63
                    }

        self.freesuffer_to_label = {0: 0, 2: 1, 3: 2, 4: 3, 7: 4, 8: 5, 10: 6, 11: 7, 12: 8, 13: 9,
                           14: 10, 15: 11, 16: 12, 17: 13, 18: 14, 24: 15, 28: 16, 31: 17, 41: 18, 42: 19,
                           43: 20, 46: 21, 47: 22, 49: 23, 50: 24, 51: 25, 52: 26, 53: 27, 54: 28, 60: 29,
                           63: 30}

        self.label_to_freesurffer = {0: 0, 1: 2, 2: 3, 3: 4, 4: 7, 5: 8, 6: 10, 7: 11, 8: 12, 9: 13,
                           10: 14, 11: 15, 12: 16, 13: 17, 14: 18, 15: 24, 16: 28, 17: 31, 18: 41, 19: 42,
                           20: 43, 21: 46, 22: 47, 23: 49, 24: 50, 25: 51, 26: 52, 27: 53, 28: 54, 29: 60,
                           30: 63}

        self.colormap2 = [[0, 0, 0], [127, 246, 186], [9, 67, 74], [230, 175, 171], [215, 179, 46],
            [218, 5, 237], [31, 79, 47], [30, 29, 190], [92, 193, 84], [19, 135, 41],
            [178, 85, 254], [231, 67, 75], [159, 30, 110], [202, 40, 203], [224, 10, 242],
            [93, 212, 121], [105, 223, 100], [20, 162, 66], [126, 68, 43], [117, 20, 188],
            [87, 79, 222], [73, 115, 226], [145, 38, 121], [99, 133, 38], [200, 167, 109],
            [213, 128, 61], [53, 51, 1], [13, 238, 66], [86, 226, 252], [137, 24, 163],
            [236, 248, 83]
        ]

        self.colormap = [[0, 0, 0], [0, 0, 255],  [0, 0, 255],  [0, 0, 255],  [0, 0, 255],
            [0, 0, 255], [0, 0, 255], [0, 0, 255], [0, 0, 255], [0, 0, 255],
            [0, 0, 255], [0, 0, 255], [0, 0, 255], [0, 0, 255], [0, 0, 255],
            [0, 0, 255], [0, 0, 255], [0, 0, 255], [0, 0, 255], [0, 0, 255],
            [0, 0, 255], [0, 0, 255], [0, 0, 255], [0, 0, 255], [0, 0, 255],
            [0, 0, 255], [0, 0, 255], [0, 0, 255], [0, 0, 255], [0, 0, 255],
            [0, 0, 255]
        ]

    def drop_label(self, brain_image, drop_list):
        for drop_idx in drop_list:
            brain_image[np.where(brain_image == drop_idx)] = 0
        return brain_image

    def seg_recoloring(self, seg_image):
        orig_shape = np.shape(seg_image)
        color_image = np.zeros((orig_shape[0], orig_shape[1], orig_shape[2], 3))
        cnt = 0
        for x in range(0, orig_shape[0]):
            for y in range(0, orig_shape[1]):
                for z in range(0, orig_shape[2]):
                    color = self.colormap[self.freesuffer_to_label[int(seg_image[x, y, z])]]

                    color_image[x, y, z, 0] = color[0]
                    color_image[x, y, z, 1] = color[1]
                    color_image[x, y, z, 2] = color[2]
        print(cnt)
        return color_image

    def graytorgb(self, image):
        gray_shape = np.shape(image)
        gray_img = image
        gray_img = np.reshape(gray_img, (gray_shape[0], gray_shape[1], gray_shape[2], 1))

        color_image = np.concatenate((gray_img, gray_img, gray_img), axis=3)

        return color_image

    def get_segmentation_infos(self, brainmask_img, file_name):

        # Load segmentation image
        seg_file_path = self.search_dir + file_name

        #npy version
        #aseg_img = np.load(seg_file_path + '.npy')
        #nii version
        aseg_noCCseg = nib.load(seg_file_path)
        aseg_img = aseg_noCCseg.get_fdata()
        print("seg_file_path : "+ seg_file_path)
        # rotate
        brainmask_img = np.transpose(brainmask_img, (1, 2, 0))
        # Already done
        aseg_img = np.transpose(aseg_img, (1, 2, 0))

        s1, e1, s2, e2, s3, e3 = cut_brain(brainmask_img, only_index = True)

        brainmask = brainmask_img[s1:e1, s2:e2, s3:e3]

        # Already done
        aseg_img = aseg_img[s1:e1, s2:e2, s3:e3]
        shape = np.shape(aseg_img)

        # Drop labels
        label_map = self.drop_label(aseg_img, self.drop_list)

        # Get unique aseg_image
        unique, counts = np.unique(label_map, return_counts = True)
        volume_map = []
        for i in unique:
            brain_region = self.labeled_dict[int(i)]
            volume = counts[self.freesuffer_to_label[int(i)]]
            volume_map.append([i, brain_region, volume])

        # extension brainmask_image 1(grey)->3(rgb)
        color_brain_img = self.graytorgb(brainmask)
        color_aseg_img = self.seg_recoloring(label_map)

        return [volume_map, brainmask, color_brain_img, color_aseg_img, label_map]

    def extract_region(self, label_map, drop_list=[]):
        label_map = self.drop_label(label_map, drop_list)
        color_aseg_img = self.seg_recoloring(label_map)
        return color_aseg_img

    def get_labeled_dict(self):
        return self.labeled_dict

    def get_freesurfer_to_label(self):
        return self.freesuffer_to_label


