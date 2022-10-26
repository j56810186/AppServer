from sklearn.cluster import KMeans
from collections import Counter
from matplotlib import pyplot as plt
import cv2

from .hex2colorname import findcolorname

# Utility function, rgb to hex
def rgb2hex(rgb):
    hex = "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
    return hex

def find_main_color(path, k=6):
    # load image
    img_bgr = cv2.imread(path)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    # resize image to speed up processing time
    resized_img_rgb = cv2.resize(img_rgb, (64, 96), interpolation=cv2.INTER_AREA)
    crop_img = resized_img_rgb[int(20):int(52), int(20):int(52)] #一般衣服，褲子可能會背景太多
    # crop_img = resized_img_rgb[int(20):int(52), int(32):int(64)]
    # reshape the image to be a list of pixels
    img_list = crop_img.reshape((crop_img.shape[0] * crop_img.shape[1], 3))
    # cluster the pixels and assign labels
    clt = KMeans(n_clusters=k)
    labels = clt.fit_predict(img_list)

    # count labels to find most popular
    label_counts = Counter(labels)
    main_colorID = max(label_counts, key=label_counts.get)
    # subset out most popular centroid
    center_colors = list(clt.cluster_centers_)
    # find the most popular color by hex code
    main_color = center_colors[main_colorID]
    main_color = main_color.astype(int)
    color_hex = rgb2hex(main_color)

    # plots
    # plt.figure(figsize=(14, 8))
    # plt.subplot(221)
    # plt.imshow(resized_img_rgb)
    # plt.axis('off')

    # plt.show()

    return color_hex
    # print(color_labels)

def colorClassify(img_path):
    return findcolorname(find_main_color(img_path))

# read jpg/png img
# print(colorClassify('IMG_8814.jpg'))
