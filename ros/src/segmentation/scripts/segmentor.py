#
# Semantic Segmentator
# Class for driving image segmentation
# Integrated in drive.py. For more
# information see README.md.
# ------------------------------------
# Neil Nie & Michael Meng
# (c) Yongyang Nie 2018

from keras import backend as K
from models.icnet import ICNet
import utils as utils
import configs as configs
import cv2
import numpy as np
import tensorflow as tf


class Segmentor():

    def __init__(self, weight_path):

        K.clear_session()

        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        sess = tf.Session(config=config)
        K.set_session(sess)

        self.model = ICNet(width=configs.img_width, height=configs.img_height, n_classes=configs.nb_classes,
                           weight_path=weight_path, training=False)

        # self.model = ICNet(width=configs.img_width, height=configs.img_height, n_classes=configs.nb_classes,
        #                    weight_path=weight_path, training=True, mode='cross_fusion')
        print(self.model.model.summary())
        self.backgrounds = self.load_color_backgrounds()

    @staticmethod
    def load_color_backgrounds():

        backgrounds = []

        for i in range(len(utils.labels)):
            color = utils.labels[i][7]

            bg = np.zeros((720, 1280, 3), dtype=np.uint8)
            bg[:, :, 0].fill(color[2])
            bg[:, :, 1].fill(color[1])
            bg[:, :, 2].fill(color[0])
            backgrounds.append(bg)

        return backgrounds

    def semantic_segmentation(self, image, depth_image, visualize=False):

        # parameters
        # image: input image
        # visualize: whether to visualize the segmentation results
        # return
        # output: output of ConvNet
        # img_pred: visualization

        image = cv2.resize(image, (configs.img_width, configs.img_height))
        x = np.array([cv2.cvtColor(image, cv2.COLOR_BGR2RGB)])
        output = self.model.model.predict([x])[0]

        # image = cv2.resize(image, (configs.img_width, configs.img_height))
        # depth_image = cv2.resize(depth_image, (configs.img_width, configs.img_height))
        #
        # x = np.array([cv2.cvtColor(image, cv2.COLOR_BGR2RGB)])
        # x_depth = np.array([depth_image])
        #
        # output = self.model.model.predict([x, x_depth])[0][0]

        if visualize:
            im_mask = self.convert_class_to_rgb(image_labels=output)
            viz = cv2.addWeighted(im_mask, 1.0, cv2.resize(image, (1280, 720)), 0.8, 0)
            viz = cv2.resize(viz, (1280, 720))
            return output, viz
        else:
            return output, None

    def convert_class_to_rgb(self, image_labels, threshold=0.50):

        # convert any pixel > threshold to 1
        # convert any pixel < threshold to 0
        # then use bitwise_and

        output = np.zeros((720, 1280, 3), dtype=np.uint8)

        for i in range(configs.nb_classes):
            split = image_labels[:, :, i]
            split[split > threshold] = 1
            split[split < threshold] = 0
            split[:] *= 255
            split = cv2.resize(split.astype(np.uint8), (1280, 720))

            res = cv2.bitwise_and(self.backgrounds[i], self.backgrounds[i], mask=split)

            output = cv2.addWeighted(output, 1.0, res, 1.0, 0)

        return output
