import numpy as np
import nibabel as nib
import torch
import csv
import shutil
import cv2
import matplotlib.pyplot as plt
import os
from scipy.ndimage.filters import gaussian_filter
#import SimpleITK as sitk
import matplotlib.pyplot as plt


def Draw_rect(img_array, color=[]):
    s1, s2, s3 = np.shape(img_array)
    img_array[0:s1, 0] = color
    img_array[0, 0:s2] = color
    img_array[0:s1, s2 - 1] = color
    img_array[s1 - 1, 0:s2] = color
    return img_array

def rgbtogray(image):
    image_shape = np.shape(image)
    gray_image = np.reshape(image[:,:,:,0],(image_shape[0],image_shape[1],image_shape[2]))
    return gray_image

def graytorgb(image):
    gray_shape = np.shape(image)
    gray_img = image
    gray_img = np.reshape(gray_img, (gray_shape[0], gray_shape[1], gray_shape[2], 1))

    color_image = np.concatenate((gray_img, gray_img, gray_img), axis=3)

    return color_image

def cvshow(volume, print_str="", axis_index=1, saved_path = ""):
    print(print_str)
    axis = np.shape(volume)[axis_index-1]
    for i in range(0, axis):

        if cv2.waitKey(40) & 0xFF == ord('n'):
            break

        if axis_index == 1:
            cv2.imshow('image', volume[i, :, :])
            image = cv2.resize(volume[i, :, :],(300, 300))
            cv2.imwrite(saved_path + "_" + str(i) + ".jpg", image)
        elif axis_index == 2:
            cv2.imshow('image', volume[:, axis - i -1, :])
            image = cv2.resize(volume[:, axis - i -1, :], (300, 300))
            cv2.imwrite(saved_path + "_" + str(i) + ".jpg", image)
        else:
            cv2.imshow('image', volume[:, :, i])
            image = cv2.resize(volume[:, :, i], (300, 300))
            cv2.imwrite(saved_path + "_" + str(i) + ".jpg", image)

def graytorgb(image):
    gray_shape = np.shape(image)
    gray_img = image
    gray_img = np.reshape(gray_img, (gray_shape[0], gray_shape[1], gray_shape[2], 1))

    color_image = np.concatenate((gray_img, gray_img, gray_img), axis=3)

    return color_image
def Brainmask_preprocessing(brainmask_img):
    # rotate
    brainmask_img = np.transpose(brainmask_img, (1, 2, 0))
    s1, e1, s2, e2, s3, e3 = cut_brain(brainmask_img, only_index=True)
    brainmask = brainmask_img[s1:e1, s2:e2, s3:e3]
    return brainmask

def Normalize(brain_image):
    return (brain_image - np.min(brain_image)) / (np.max(brain_image) - np.min(brain_image))


def reshape_3D(img_in, new_shape=(160,192,224) , interpo=cv2.INTER_CUBIC):
    img_out_buffer = np.zeros(shape=(img_in.shape[0], new_shape[1], new_shape[2]), dtype=float)
    img_out_buffer2 = np.zeros(shape=(new_shape[2], new_shape[1], new_shape[0]), dtype=float)

    for i in range(img_in.shape[0]):
        img_buffer = img_in[i]
        img_buffer2 = cv2.resize(img_buffer, (new_shape[2], new_shape[1]), interpolation=interpo)
        img_out_buffer[i] = img_buffer2
    img_out_buffer = np.transpose(img_out_buffer, (2, 1, 0))

    for j in range(img_out_buffer.shape[0]):
        img_buffer3 = img_out_buffer[j]
        img_buffer4 = cv2.resize(img_buffer3, (new_shape[0], new_shape[1]), interpolation=interpo)
        img_out_buffer2[j] = img_buffer4
    img_out = np.transpose(img_out_buffer2, (2, 1, 0))
    return img_out

def reshape_4D(img_in, new_shape=(160,192,224,3) , interpo=cv2.INTER_CUBIC):
    img_out_buffer = np.zeros(shape=(img_in.shape[0], new_shape[1], new_shape[2]), dtype=float)
    img_out_buffer2 = np.zeros(shape=(new_shape[2], new_shape[1], new_shape[0]), dtype=float)

    for i in range(img_in.shape[0]):
        img_buffer = img_in[i]
        img_buffer2 = cv2.resize(img_buffer, (new_shape[2], new_shape[1]), interpolation=interpo)
        img_out_buffer[i] = img_buffer2
    img_out_buffer = np.transpose(img_out_buffer, (2, 1, 0))

    for j in range(img_out_buffer.shape[0]):
        img_buffer3 = img_out_buffer[j]
        img_buffer4 = cv2.resize(img_buffer3, (new_shape[0], new_shape[1]), interpolation=interpo)
        img_out_buffer2[j] = img_buffer4
    img_out = np.transpose(img_out_buffer2, (2, 1, 0))
    return img_out

def cut_brain(brain_img, maintain = False, only_index = False):
    img = brain_img
    axis_1, axis_2, axis_3 = brain_img.shape

    ##############################################################
        # Right to Left  Sagittal
    ##############################################################

    axis1_start, axis1_end = [0, 0]
    axis2_start, axis2_end = [0, 0]
    axis3_start, axis3_end = [0, 0]

    for i in range(0, axis_1):
        slice = img[i, :, :]
        if np.max(slice) != 0:
            axis1_start = i
            break

    for i in range(axis_1-1,0,-1):
        slice = img[i, :, :]
        if np.max(slice) != 0:
            axis1_end = i
            break

    for i in range(0, axis_2):
        slice = img[:, i, :]
        if np.max(slice) != 0:
            axis2_start = i
            break
    for i in range(axis_2-1, 0, -1):
        slice = img[:, i, :]
        if np.max(slice) != 0:
            axis2_end = i
            break

    for i in range(0, axis_3):
        slice = img[:, :, i]
        if np.max(slice) != 0:
            axis3_start = i
            break
    for i in range(axis_3-1, 0, -1):
        slice = img[:, :, i]
        if np.max(slice) != 0:
            axis3_end = i
            break
    if only_index == True:
        return [axis1_start, axis1_end, axis2_start, axis2_end, axis3_start, axis3_end]

    if maintain == True:
        axis1_sub = axis1_end - axis1_start
        axis2_sub = axis2_end - axis2_start
        axis3_sub = axis3_end - axis3_start
        max_ = np.max(np.array([axis1_sub, axis2_sub, axis3_sub]))

        gap = int(max_/2)

        axis1_mid = int((axis1_end + axis1_start)/2)
        axis2_mid = int((axis2_end + axis2_start)/2)
        axis3_mid = int((axis3_end + axis3_start)/2)

        #revised_ = np.asarray(img[axis1_start:axis1_end, axis2_start:axis2_end, axis3_start:axis3_end])
        revised_ = brain_img[axis1_mid - gap: axis1_mid + gap,\
                             axis2_mid - gap: axis2_mid + gap,\
                             axis3_mid - gap: axis3_mid + gap]
        return revised_
    else:
        revised_ = brain_img[axis1_start : axis1_end,
                            axis2_start : axis2_end,
                            axis3_start : axis3_end]
        return revised_

def cutting_meaningless_area2(brain_image,interpo=cv2.INTER_CUBIC):
    axis_1, axis_2, axis_3 = brain_image.shape

    ##############################################################
        # Right to Left  Sagittal
    ##############################################################
    brain_dat = []
    for i in range(0, axis_1):
        img2 = brain_image[i, :, :]

        if np.max(img2) == 0:
            continue
        # Normalize
        brain_dat.append(img2)
    revised_ = np.asarray(brain_dat)

    ##############################################################
        # Up to Down  Coronal
    ##############################################################
    brain_dat = []
    for i in range(0,axis_2):
        img2 = revised_[:, i, :]

        if np.max(img2) == 0:
            continue
        brain_dat.append(img2)
    revised_ = np.asarray(brain_dat)

    ##############################################################
        # Front to Back  Axial
    ##############################################################
    brain_dat = []
    for i in range(0,axis_3):
        img2 = revised_[:, :, i]
        if np.max(img2) == 0:
            continue
        brain_dat.append(img2)
    revised_ = np.asarray(brain_dat)
    # val (110,110,110)
    #return revised_
    return resize_3D(revised_,interpo=interpo, scale=256)


def resize_3D(img_in,interpo = cv2.INTER_CUBIC,scale=110):
    #scale=110
    img_out_buffer=np.zeros(shape=[img_in.shape[0],scale,scale], dtype=float)
    img_out_buffer2=np.zeros(shape=[scale,scale,scale])
    img_out= np.zeros(shape=[scale, scale, scale], dtype=float)

    for i in range(img_in.shape[0]):
        img_buffer=img_in[i]
        img_buffer2=cv2.resize(img_buffer,(scale,scale), interpolation=interpo)
        img_out_buffer[i]=img_buffer2
    img_out_buffer=np.transpose(img_out_buffer,(2,1,0))

    for j in range(scale):
        img_buffer3=img_out_buffer[j]
        img_buffer4=cv2.resize(img_buffer3,(scale,scale), interpolation=interpo)
        img_out_buffer2[j]=img_buffer4
    img_out = np.transpose(img_out_buffer2, (2,1,0))

    return img_out


def nii_intensity_norm(nii_img): #nii_img from get_fdata()
    mean = nii_img.mean()
    std = nii_img.std()
    intensity_normed_data = (nii_img - mean)/std
    return intensity_normed_data


def center_crop(input_array, scale): #input_array to be 3 dimension
    x_center= int(input_array.shape[0]/2)
    y_center= int(input_array.shape[1]/2)
    z_center= int(input_array.shape[2]/2)
    x_from= x_center - int(scale/2)
    x_to = x_center + int(scale/2)
    y_from = y_center - int(scale/2)
    y_to = y_center + int(scale/2)
    z_from = z_center - int(scale/2)
    z_to = z_center + int(scale/2)
    output_tensor = input_array[x_from:x_to, y_from:y_to, z_from:z_to]

    return output_tensor


def nii_to_tensor(data_path):
    img=nib.load(data_path)
    buffer=img.get_fdata()
    buffer=np.copy(buffer, order="C")
    _tensor=torch.from_numpy(buffer)
    return _tensor


def train_plot(epoch, loss):
    plt.plot(epoch,loss)
    plt.xlabel=('Step')
    plt.ylabel=('Loss')
    plt.title=('Train Monior')
    plt.draw()
    plt.pause(0.00001)
    plt.clf()

def train_plot_2(epoch, y1,y2,x_label="",y_label="",mode ="", title=""):
    plt.plot(epoch,y1,label=mode)
    plt.plot(epoch,y2,label=mode)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.show()
    #plt.draw()
    #plt.pause(0.00001)
    #plt.clf()

def save_figure(epoch, y1, y2, x_label="", y_label="", title="", file_path=""):
    plt.plot(epoch, y1, label="train")
    plt.plot(epoch, y2, label="test")
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.legend()
    plt.savefig(file_path,dpi=300)
    #plt.show()
    #plt.draw()
    #plt.pause(0.00001)
    plt.clf()

# raw data path + label
def data_setting(data_path, label_path): #get unique data set from raw data set
    unique_subject_lst=[] #941_S_1311
    unique_label_lst=[] #AD
    unique_process_lst=[]

    subject_lst=[] #941_S_1311
    label_lst=[] #AD
    process_lst=[]
    acq_list =[]
    with open(label_path+'adni_abstract_origin_label.csv', "r") as f:

        for line in f.readlines():
            data_key, subject, label, process,_,acq_date = line.strip().split(',')
            subject_lst.append(subject)
            label_lst.append(label)
            process_lst.append(process)
            acq_list.append(acq_date)
        f.close()
    print('csv imformation loaded')

    num_data=len(subject_lst)
    i=0
    while(1):
        pivot = 1
        while(1):
            if((subject_lst[i]!=subject_lst[i+pivot]) or (i==1721)):
                unique_subject_lst.append(subject_lst[i])
                unique_label_lst.append(label_lst[i])
                unique_process_lst.append(process_lst[i])
                i=i+pivot
                pivot=1
                break
            elif(subject_lst[i]==subject_lst[i+pivot]):
                pivot+=1

        if (i==1721):
            break
    print('unique label search done!')

    file_list=os.listdir(data_path+'origin_total_datum/')
    print('file list: "{}"'.format(file_list))
    unique_size=len(unique_subject_lst)
    img_size=len(file_list)
    print(unique_size)
    print(img_size)

    for i in range(unique_size):
        for j in range(img_size):
            if unique_subject_lst[i] in file_list[j]:
                shutil.copy(data_path+'origin_total_datum/'+file_list[j], data_path+'unique_datum/'+file_list[j])
                break
    print('unique data copy done!')
    # now, write csv
    with open(label_path+'unique_label.csv',"w") as p:
        wp = csv.writer(p)
        for m in range(len(unique_label_lst)):
            wp.writerow([unique_subject_lst[m],unique_label_lst[m], unique_process_lst[m]])
        p.close()

    print('data setting done!')

def preprocessing(brain_mri):
    brain_mri = np.transpose(brain_mri, (1, 2, 0))
    s1, e1, s2, e2, s3, e3 = cut_brain(brain_mri, only_index=True)
    brain_mri = brain_mri[s1:e1, s2:e2, s3:e3]
    reshape_brain = reshape_3D(brain_mri, new_shape=(110, 110, 110), interpo=cv2.INTER_LINEAR)
    preprocessed_brain = nii_intensity_norm(reshape_brain)
    return preprocessed_brain
'''
def preprocessing(in_array):
    array_110=resize_3D(in_array)
    g_subtracted=array_110 - gaussian_filter(array_110, sigma=1)
    img_buf = sitk.GetImageFromArray(np.copy(g_subtracted))
    img_histo = sitk.AdaptiveHistogramEqualization(img_buf)
    clahe_img = sitk.GetArrayFromImage(img_histo)[:, :, :, None]
    clahe_img = np.squeeze(clahe_img)
    normed_img = nii_intensity_norm(clahe_img)
    return normed_img
'''

def split_data():
    center_path='/home/geonuk/workhard/data/ADNI/'
    data=sorted(os.listdir(center_path+'Aligned_500'))
    num_img=len(data)
    label_list=[]
    subject_list=[]
    total_subject_list=[]
    total_label_list=[]
    with open(center_path+'/tiny_unique_label_except_black3.csv', "r") as f:
        for line in f.readlines():
            subject, label= line.strip().split(',')
            label_list.append(label)
            subject_list.append(subject)
    for i in range(num_img):
        if label_list[i]=='AD':
            total_subject_list.append(subject_list[i])
            total_label_list.append(label_list[i])
            shutil.copy(center_path+'Aligned_500/' + data[i], center_path + 'TrainData/AD/' + data[i])
        elif label_list[i]=='CN':
            shutil.copy(center_path+'Aligned_500/' + data[i], center_path + 'TrainData/CN/' + data[i])
        else:
            shutil.copy(center_path+'Aligned_500/' + data[i], center_path + 'TrainData/MCI/' + data[i])

    #with open(center_path + 'train_data/total_190/except_MCI_unique_label2.csv', "w") as p:
    #    wp = csv.writer(p)
    #    for m in range(len(total_label_list)):
    #        wp.writerow([total_subject_list[m],total_label_list[m]])
    #    p.close()

def get_max_class(score_list):
    for i in range(len(score_list)):
        if score_list[i]==max(score_list):
            max_class_id=i
    return max_class_id

def count_output(max_list):
    count_list=[0,0,0]
    for i in range(len(max_list)):
        if max_list[i]==0:
            count_list[0]+=1
        elif max_list[i]==1:
            count_list[1]+=1
        else:
            count_list[2]+=1
    return count_list

# vlfdy
def select_MCI():
    center_path='/home/geonuk/workhard/data/ADNI/'
    data=sorted(os.listdir(center_path+'processed_unique'))
    num_img=len(data)
    label_list=[]
    subject_list=[]
    with open(center_path+'tiny_unique_label_except_black3.csv', "r") as f:
        for line in f.readlines():
            subject, label= line.strip().split(',')
            label_list.append(label)
            subject_list.append(subject)
    for i in range(num_img):
        if label_list[i]=='MCI':
            shutil.copy(center_path+'processed_unique/' + data[i], center_path + 'train_data/MCI/' + data[i])
            with open(center_path + 'train_data/MCI_unique_label.csv', "w") as p:
                wp = csv.writer(p)
                for m in range(len(label_list)):
                    wp.writerow([subject_list[m],label_list[m]])
                p.close()

def LR_decay(optz, epoch, LR):
    lr=LR*0.5*epoch//10
    for param_group in optz.param_groups:
        param_group['lr'] = lr
