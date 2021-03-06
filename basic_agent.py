import numpy as np
from random import *
import heapq

'''
This is the basic agent class which has functions necessary for the basic agent's implementation
Authors: Ashwin Haridas, Ritin Nair
'''

class Point:
    def __init__(self, rgb, clusterNum):
        self.rgb = rgb
        self.clusterNum = clusterNum

'''
This function calculates the euclidean distance between two vectors
'''
def euclidean_distance(a, b):
    return np.linalg.norm(b - a)

'''
This function runs the k-means algorithm on an image
'''
def k_means(img):
    imgArr = np.empty((img.shape[0], img.shape[1]), dtype = Point)
    clusters = []
    
    # convert each pixel to a point
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            imgArr[i][j] = Point(img[i][j], -1)
        
    # randomize initial centroids
    for i in range(5):
        x = randint(0, img.shape[0] - 1)
        y = randint(0, img.shape[1] - 1)
        clusters.append(img[x][y])
        
    while True:
        # reassign point to cluster
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                shortest_distance = 500
                cluster = 0

                for x in range(5):
                    euclidean = euclidean_distance(imgArr[i][j].rgb, clusters[x])
                    if euclidean < shortest_distance:
                        shortest_distance = euclidean
                        cluster = x
                
                imgArr[i][j].clusterNum = cluster

        oldCenters = []

        for x in range(5):
            numPoints = 0
            sumR = 0
            sumG = 0
            sumB = 0

            for i in range(imgArr.shape[0]):
                for j in range(imgArr.shape[1]):
                    if imgArr[i][j].clusterNum == x:
                        sumR += imgArr[i][j].rgb[0]
                        sumG += imgArr[i][j].rgb[1]
                        sumB += imgArr[i][j].rgb[2]
                        numPoints += 1
            
            oldCenters.append(clusters[x])
            
            # find new centers
            if numPoints != 0:
                clusters[x][0] = sumR / numPoints
                clusters[x][1] = sumG / numPoints
                clusters[x][2] = sumB / numPoints
        
        oldCtr = 0

        for i in range(5):
            if abs(oldCenters[i][0] - clusters[i][0]) < 0.1:
                oldCtr += 1
            if abs(oldCenters[i][1] - clusters[i][1]) < 0.1:
                oldCtr += 1
            if abs(oldCenters[i][2] - clusters[i][2]) < 0.1:
                oldCtr += 1
        

        if oldCtr == 15:
            break
            
        
    
    return imgArr, clusters

'''
This function recolors the left side in 5 representative colors
'''
def recolor_left(left, k_means_left, clusters):
    recolored_left = np.copy(left)
    for i in range(left.shape[0]):
        for j in range(left.shape[1]):
            cluster = k_means_left[i][j].clusterNum
            recolored_left[i][j] = clusters[cluster]
    
    return recolored_left

'''
This function returns a patch for a given pixel
'''
def pixel_to_patch(arr, i, j): # find a 3x3 patch given indices of an array
    pixel_indices = []
    patch = np.empty((3, 3)) 
    patchX = 0
    patchY = 0
    for x in range (i - 1, i + 2):
        patchY = 0
        for y in range (j - 1, j + 2):
            patch[patchX][patchY] = arr[x][y][0]
            pixel_indices.append((x,y)) 
            patchY += 1
        patchX += 1
    return patch.flatten(), pixel_indices  # patch stores gray value and the index of the pixel

'''
This function returns a list of 1000 random patches
'''
def get_patch_list (bw_left):
    result = []
    used = []
    while(len(result) < 1000):
        i = randint(1, bw_left.shape[0] - 2)
        j = randint(1, bw_left.shape[1] - 2)
        if ((i, j) not in used):
            result.append(pixel_to_patch(bw_left, i, j))
            used.append((i, j))
    return result
    
'''
This function gets the six most similar patches to a given patch
'''
def six_similar (patch, bw_left):
    similar = []
    result = []
    selected_patches = get_patch_list(bw_left)
    for i in range (len(selected_patches)):
        selected_patch, selected_indices = selected_patches[i]
        difference = euclidean_distance(patch, selected_patch)
        heapq.heappush(similar, (difference, selected_indices))

    for count in range(6):
        difference, training_indices = heapq.heappop(similar)
        result.append(training_indices)
    return result # list of 6 most similar patches

'''
This returns the colored pixel givena a black and white patch
'''
def choose_pixel_color (training_indices, clusters, k_means_left):
    count_list = []
    for i in range (len(clusters)):
        count_list.append(0)

    for i in range(6):
        training_index = training_indices[i]
        index = training_index[4] # to get information about middle pixel in the patch
        x, y = index
        cluster = k_means_left[x][y].clusterNum
        count_list[cluster] += 1

    maxCount = 0
    maxIndex = -1

    for i in range(len(count_list)):
        if count_list[i] > maxCount:
            maxCount = count_list[i]
            maxIndex = i
    hasTie = False
    for i in range(len(count_list)):
        if i != maxIndex:
            if maxCount == count_list[i]:
                hasTie = True
                break
    
    if(not hasTie):
        return clusters[maxIndex]
    else: # if there is a tie pick the representative color of the middle pixel of the most similar patch
        training_index = training_indices[0]
        index = training_index[4] # to get information about middle pixel in the patch
        x, y = index
        cluster = k_means_left[x][y].clusterNum
        return clusters[cluster]

'''
This function recolors the right side
'''
def recolor_right(bw_left, bw_right, k_means_left, clusters):
    recolored_count = 0
    recolored_right = np.copy(bw_right)
    for i in range (bw_right.shape[0]):
        for j in range(bw_right.shape[1]):
            if i == 0 or j == 0 or i == bw_right.shape[0] - 1 or j == bw_right.shape[1] - 1: # border cell to recolor black
                recolored_right[i][j][0] = 0
                recolored_right[i][j][1] = 0
                recolored_right[i][j][2] = 0
                continue
            # get the patch of nine pixels with the current pixel as the middle
            curr_patch, pixel_indices = pixel_to_patch(bw_right, i, j) 
            training_indices = six_similar(curr_patch, bw_left)
            color = choose_pixel_color(training_indices, clusters, k_means_left)
            recolored_right[i][j] = color
            recolored_count += 1
            print(recolored_count)
    return recolored_right