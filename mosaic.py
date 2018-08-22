# This program creates a mosaic of a target image out of tile images.
# This program only uses each tile image once.
# For more information, read the READ_ME.txt

import sys
import math
import numpy as np
import cv2
import random
import os
import glob
import random
from fractions import gcd

def main(targ, tiles):
  # prompt the user for the requested resulting size and aspect ratio of the mosaic
  target, images, res_size = prompt(targ, tiles)
  
  # get the dimensions of the target and tile images
  target_len, target_wid, a = np.shape(target)
  img_len, img_wid, a = np.shape(images[0])
  
  # resize the tile images if necessary and the target image to fit them
  images, num_x, num_y, img_wid, img_len = resizeImages(images, img_wid, img_len, target_wid, target_len)
  target, num_x, num_y = resizeTarget(target, images, num_x, num_y, img_wid, img_len)
   
  # contains the Euclidean distance sums of each image
  sums = calculateSums(target, images, num_x, num_y, img_wid, img_len)

  # resulting image
  res = np.zeros((num_y * img_len, num_x * img_wid, 3))
  
  # stores the location of tile images after randomly placing them
  tracker = setInitialTiles(images, res, num_y, num_x, img_wid, img_len)

  # swap around the tiles at random to see if it makes an improvement
  swap(res, tracker, images, sums, num_y, num_x, img_wid, img_len)
  
  # resize the finished mosaic and save it
  res = cv2.resize(res, dsize=(target_wid * res_size, target_len * res_size), interpolation=cv2.INTER_NEAREST)
  cv2.imwrite(targ[:-4] + "_mosaic.jpg", res)

  # erase the resized tile images
  deleteTiles()


# prompt the user for the images to be used, as well as the wanted shape of the resulting mosaic
def prompt(targ, tiles):
  print("Enter the preferred size of the resulting mosaic (1, 2, or 3).")
  print("\t 1 - Original (same size as the target image)")
  print("\t 2 - 2x Dimensions")
  print("\t 3 - 3x Dimensions")
  res_size = int(input())
  
  # read in the images
  images = [cv2.imread(file) for file in glob.glob(tiles + "/*")]
  target = cv2.imread(targ)

  return target, images, res_size


# resize the tile images to best fit the mosaic
def resizeImages(images, img_wid, img_len, res_wid, res_len):
  # get the counts of how many tile images can fit in the target image
  num_x = int(round(res_wid / img_wid))
  num_y = int(round(res_len / img_len))
  
  resized = False
  
  # make the tile images larger if there are not enough images to create the mosaic
  while num_x * num_y > len(images):
    resized = True
    img_len *= 2
    img_wid *= 2
    num_x = int(round(res_wid / img_wid))
    num_y = int(round(res_len / img_len))
  
  # make the tile images smaller if we have enough images in order to maximize how many are used
  while ((img_len > 100 or img_wid > 100) and (num_x * num_y) * 4 < len(images)):
    resized = True
    img_len //= 2
    img_wid //= 2
    num_x = int(round(res_wid / img_wid))
    num_y = int(round(res_len / img_len))

  if resized:
    # if there's not a folder of resized tile images already, make one
    directory = os.path.dirname(os.path.realpath(__file__)) + "/fixed/"
    if not os.path.exists(directory):
      os.makedirs(directory)
    # if there is a folder, clear its contents
    else:
      files = glob.glob('fixed/*')
      for f in files:
        os.remove(f)
        
    count = 0
    # create new tile images with the better sizes
    for image in images:
      resized = cv2.resize(image, dsize=(img_wid, img_len), interpolation=cv2.INTER_NEAREST)
      cv2.imwrite("fixed/" + str(count) + ".jpg", resized)
      count += 1
    images = [cv2.imread(file) for file in glob.glob("fixed/*.jpg")]
    
  return images, num_x, num_y, img_wid, img_len


# resize the target image to best fit the tile images
def resizeTarget(target, images, num_x, num_y, img_wid, img_len):
  # resizing
  denom = gcd(num_x, num_y)
  add_x = num_x // denom
  add_y = num_y // denom
  
  while (num_x + add_x) * (num_y + add_y) < len(images):
    num_x += add_x
    num_y += add_y
  
  num_images_used = num_x * num_y
  
  print("Using " + str(num_images_used) + " images")
  
  # give the recommended number of images if below 400
  num_x_rec = num_x
  num_y_rec = num_y
  if (num_images_used < 400):
    while (num_images_used < 400):
      num_x_rec += add_x
      num_y_rec += add_y
      num_images_used = num_x_rec * num_y_rec
    print("It is recommended to have at least " + str(num_images_used) + " tile images for your image set")
    
  target = cv2.resize(target, dsize=(num_x * img_wid, num_y * img_len), interpolation=cv2.INTER_NEAREST)
  return target, num_x, num_y


# calculate the Euclidean distance sums for each tile image, respective to every possible position on the mosaic
def calculateSums(target, images, num_x, num_y, img_wid, img_len):
  num_images_used = num_x * num_y
  
  # contains the Euclidean distance sums
  sums = [[[0 for k in range(num_images_used)] for j in range(num_x)] for i in range(num_y)]
  sums = np.array(sums,dtype='float')
  for img in range(num_images_used):
    for k in range(num_y):
      for l in range(num_x):
        sum = np.sqrt(calculateDistance(target[k * img_len:k * img_len + img_len,l * img_wid:l * img_wid + img_wid], images[img][:][:]))

        sums[k][l][img] += sum
  return sums
       
          
# sets the initial tiles randomly and keep track of their placements in a tracker array
def setInitialTiles(images, res, num_y, num_x, img_wid, img_len):
  num_images_used = num_x * num_y
  arr = [i for i in range(num_images_used)]
  random.shuffle(arr)
  
  # track where each image is placed in the resulting image
  tracker = np.ndarray.tolist(np.zeros((num_y,num_x)))
  
  index = 0
  for k in range(num_y):
    for l in range(num_x):
      res[k * img_len:k * img_len + img_len,l * img_wid:l * img_wid + img_wid] = images[arr[index]]
      # Create the tracker array
      tracker[k][l] = arr[index]
      index += 1
  return tracker


# swap tiles randomly to check if it results in a better fit
def swap(res, tracker, images, sums, num_y, num_x, img_wid, img_len):
  count = 0
  # swapping algorithm
  for iter in range(1000000):
    
    # get the coordinates of two tiles at random
    row1 = random.randint(0, num_y - 1)
    col1 = random.randint(0, num_x - 1)
    row2 = random.randint(0, num_y - 1)
    col2 = random.randint(0, num_x - 1)
    
    if (row1 == row2 and col1 == col2):
      continue
    
    # get the images at those coordinates
    img1 = tracker[row1][col1]
    img2 = tracker[row2][col2]
    
    # get the Euclidean distance sums of those images in their current positions
    # and in the positions of the compared image
    sum1 = sums[row1][col1][img1]
    sum1_switch = sums[row2][col2][img1]
    sum2 = sums[row2][col2][img2]
    sum2_switch = sums[row1][col1][img2]
    
    # the combined Euclidean distance sum of the images in their current positions
    combined = sum1 + sum2
    # the combined Euclidean distance sum of the images in the compared image's positions
    combined_switch = sum1_switch + sum2_switch
    # swap the tiles
    if (combined_switch < combined):
      count += 1
      tracker[row1][col1], tracker[row2][col2] = tracker[row2][col2], tracker[row1][col1]
      res[row1 * img_len:row1 * img_len + img_len,col1 * img_wid:col1 * img_wid + img_wid] = images[img2]
      res[row2 * img_len:row2 * img_len + img_len,col2 * img_wid:col2 * img_wid + img_wid] = images[img1]  
  print("Number of swaps: " + str(count))


# deletes the newly created tile images
def deleteTiles():
  files = glob.glob('fixed/*')
  for f in files:
    os.remove(f)


# calculate the Euclidean distance
def calculateDistance(i1, i2):
  return np.sum((i1.astype('float')-i2)**2)


if __name__ == '__main__':
  if len(sys.argv) < 3:
	  print("Usage: %s <target image> <directory of tile images>\r" % (sys.argv[0],))
  else:
	  main(sys.argv[1], sys.argv[2])
  
