#import nibabel as nib
#import numpy as np
#from utility import *
from Segmentation_controller import *
#from Diagnosis_Network.model import *
class Volume_controller:
    def __init__(self, model_path):
        self.model_path = model_path
        self.volume=[]
        self.Isvol = False
        file_path = []

    # Load volume
    def Isvolume(self):
        return self.Isvol

    def Load_volume(self,path="./"):
        self.Isvol = True
        self.file_path = path
        self.file_name = path.split('/')[-1]

        print("Load data : " + self.file_name)

        '''
        if self.file_name.__contains__("AD"):
            self.index = 0
        else:
            self.index = 1
        '''

        self.seg_controllor = Segmentation_controller("../Data/ccseg/")

        # Load_volume
        brainmask = nib.load(self.file_path)
        brainmask_origin = brainmask.get_fdata()

        self.volume_map, self.grey_brainmask, self.volume, self.color_aseg_img, self.label_map = \
            self.seg_controllor.get_segmentation_infos(brainmask_origin, self.file_name)

        #self.volume = Brainmask_preprocessing(brainmask_origin)

        self.a1, self.a2, self.a3, self.a4 = np.shape(self.volume)

        # AXIS Ratio
        sum = self.a1 + self.a2 + self.a3
        self.rate_x = self.a1 / sum
        self.rate_y = self.a3 / sum
        self.rate_z = self.a2 / sum

        # AXIS Index
        self.axial_index = int(self.a1/2)
        self.coronal_index = int(self.a2/2)
        self.sagittal_index = int(self.a3/2)

        # AXIS Size
        self.axial_size = self.a1
        self.coronal_size = self.a2
        self.sagittal_size = self.a3

        # Middle Index
        self.axial_middle_index = self.axial_index
        self.coronal_middle_index = self.coronal_index
        self.sagittal_middle_index = self.sagittal_index

        # Prediction value
        self.prediction_val = [0.0, 0.0]


        print("volume_shape : " + str(self.a1) + ", " + str(self.a2) + ", " + str(self.a3) + ', ' + str(self.a4))

        print("axial_size : " + str(self.axial_size))
        print("coronal_size : " + str(self.coronal_size))
        print("sagittal_size : " + str(self.sagittal_size))

    # For opengl get 6 images

    def get_axis_volumes(self):

        ax_image = self.volume[self.axial_middle_index, :, :, :]
        co_image = self.volume[:, self.coronal_middle_index, :, :]
        sa_image = self.volume[:, :, self.sagittal_middle_index, :]

        return [ax_image, co_image, sa_image, self.axial_size, self.coronal_size, self.sagittal_size]

    def get_opengl_parameter(self):

        ax_image = self.volume[self.axial_index,:,:,:]
        ax_image = self.Draw_rect(ax_image, color=[0, 255, 0])
        ax_image = np.flipud(ax_image).copy()

        ax_image = ax_image.astype(np.uint8).copy()
        ax_image_flip = np.flipud(ax_image).copy()

        co_image = self.volume[:, self.coronal_index, :, :]
        co_image = self.Draw_rect(co_image, color=[255, 0, 0])

        co_image = co_image.astype(np.uint8).copy()
        co_image_flip = np.fliplr(co_image).copy()

        sa_image = self.volume[:, :, self.saggital_index, :]
        sa_image = self.Draw_rect(sa_image, color=[0, 0, 255])

        sa_image = sa_image.astype(np.uint8).copy()
        sa_image_flip = np.fliplr(sa_image).copy()

        return [ax_image, ax_image_flip, co_image, co_image_flip, sa_image, sa_image_flip]

        '''
        self.axial_01 = QImage(self.ax_image, self.s3, self.s2, 3 * self.s3, QImage.Format_RGB888)
        self.axial_02 = QImage(self.ax_image_flip, self.s3, self.s2, 3 * self.s3, QImage.Format_RGB888)

        self.coronal_01 = QImage(self.co_image, self.s3, self.s1, 3 * self.s3, QImage.Format_RGB888)
        self.coronal_02 = QImage(self.co_image_flip, self.s3, self.s1, 3 * self.s3, QImage.Format_RGB888)

        self.saggital_01 = QImage(self.sa_image, self.s2, self.s1, 3 * self.s2, QImage.Format_RGB888)
        self.saggital_02 = QImage(self.sa_image_flip, self.s2, self.s1, 3 * self.s2, QImage.Format_RGB888)
        '''

    def get_diagnosis(self, Threshold=0.7):
        print("MRI diagnosis...")
        #gray_image = rgbtogray(self.volume)
        shape = np.shape(self.grey_brainmask)


        '''
        predicted_label, gradcam_image = visualize_heatmap_feature(self.grey_brainmask,
                                                                   model_path=self.model_path,
                                                                   new_shape=(shape[0], shape[1], shape[2])
                                                                   ,sn=6, mix=False)
        '''
        #np.save('../Data/activation_map/' + self.file_name, gradcam_image)
        #np.save('../Data/label/' + self.file_name, predicted_label)

        gradcam_image = np.load('../Data/activation_map/' + self.file_name + '.npy')
        predicted_label = np.load('../Data/label/' + self.file_name + '.npy')

        gradcam_image = gradcam_image[...,::-1]
        #gradcam_image = np.transpose(gradcam_image, (2, 1, 0))

        gray_cam_mask = rgbtogray(gradcam_image.copy())
        gray_cam_mask[np.where(gray_cam_mask[:, :, :] < (255 * Threshold))] = 0.0
        gray_cam_mask[np.where(gray_cam_mask[:, :, :] > 0)] = 1.0

        print("Detecting damaged area")

        detected_area = gray_cam_mask * self.label_map

        # Get unique aseg_image
        unique, counts = np.unique(detected_area, return_counts = True)
        label_dict = self.seg_controllor.get_labeled_dict()
        freesuffer_to_label = self.seg_controllor.get_freesurfer_to_label()

        volume_map = []
        for i, label in enumerate(unique):
            brain_region = label_dict[int(label)]
            volume = counts[i]
            volume_map.append([int(label), brain_region, volume])

        self.volume = np.uint8(self.volume * 0.5 + gradcam_image * 0.5)
        self.prediction_val = predicted_label

        return volume_map

        #self.prediction_val = predicted_label

    def get_volume_map(self):
        return self.volume_map
    def get_prediction(self):
        return self.prediction_val
    def get_axial_size(self):
        return self.axial_size
    def get_coronal_size(self):
        return self.coronal_size
    def get_sagittal_size(self):
        return self.sagittal_size
    def get_axial_index(self):
        return self.axial_index
    def get_coronal_index(self):
        return self.coronal_index
    def get_sagittal_index(self):
        return self.sagittal_index
    def get_volume_info(self):
        return self.volume_map

    def get_axial_image(self,index):
        if index > self.a3 | index < 0:
            print("Error")
            return []
        self.axial_index = index
        return self.volume[index, :, :, :].astype(np.uint8)

    def get_coronal_image(self, index):
        if index > self.a2 | index < 0:
            print("Error")
            return []
        self.coronal_index = index
        return self.volume[:, index, :, :].astype(np.uint8)

    def get_sagittal_image(self, index):
        if index > self.a1 | index < 0:
            print("Error")
            return []


        self.sagittal_index = index
        return self.volume[:, :, index, :].astype(np.uint8)


        ###########   For 3d image   ############
        '''
        ax_image = self.brainmask_rgb[int(self.s3/2),:,:,:]
        ax_image = self.Draw_rect(ax_image, color=[0, 255, 0])
        ax_image = np.flipud(ax_image).copy()
        self.ax_image = ax_image.astype(np.uint8).copy()
        self.ax_image_flip = np.flipud(self.ax_image).copy()

        co_image = self.brainmask_rgb[:, int(self.s2 / 2), :, :]
        co_image = self.Draw_rect(co_image, color=[255, 0, 0])
        self.co_image = co_image.astype(np.uint8).copy()
        self.co_image_flip = np.fliplr(self.co_image).copy()

        sa_image = self.brainmask_rgb[:, :, int(self.s1/2), :]
        sa_image = self.Draw_rect(sa_image, color=[0, 0, 255])
        self.sa_image = sa_image.astype(np.uint8).copy()
        self.sa_image_flip = np.fliplr(self.sa_image).copy()


        self.axial_01 = QImage(self.ax_image, self.s3, self.s2, 3 * self.s3, QImage.Format_RGB888)
        self.axial_02 = QImage(self.ax_image_flip, self.s3, self.s2, 3 * self.s3, QImage.Format_RGB888)

        self.coronal_01 = QImage(self.co_image, self.s3, self.s1, 3 * self.s3, QImage.Format_RGB888)
        self.coronal_02 = QImage(self.co_image_flip, self.s3, self.s1, 3 * self.s3, QImage.Format_RGB888)

        self.saggital_01 = QImage(self.sa_image, self.s2, self.s1, 3 * self.s2, QImage.Format_RGB888)
        self.saggital_02 = QImage(self.sa_image_flip, self.s2, self.s1, 3 * self.s2, QImage.Format_RGB888)
        '''







