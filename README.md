# mosaic

This program creates a mosaic image, taking in a target image and numerous tile images. Each tile image is used at most once and they should all be of the same size and shape (every tile image will be defaulted to the same size and shape of the first one).
It uses the difference of Euclidean distance sums of every pair of an image and a portion of the target image in order to calculate which image would best fit a certain position. Since this is calculated for each image at every possible position, the cost of running the program is large, taking several minutes to complete (larger sets of tile images take longer). 
It is recommended to have at least 400 tile images. It is likely that not every image will be used, as they would not all fit in the mosaic.


## How it Works

The target image and tile images are resized to try to fit the highest number of tiles within the mosaic. 
The mosaic image is at first randomized with the tile images. 2 tiles are then randomly selected and compared to see if swapping them would result in a lower combined Euclidean distance sum, i.e. a better matching mosaic image.

For example, img1 is in position (1,1) and has a sum of 500. It has a sum of 400 at (2,2).
img2 is in position (2,2) and has a sum of 600. It has a sum of 250 at (1,1).
Where they are now, img1 and img2 have a combined 1100 sum. If they were swapped, they would have a combined 650 sum. Thus, this would indicate that the two tiles should be swapped.

Rather than calculating the Euclidean distance sum for every image at its position and comparing it with another random image at its corresponding position, the calculations are done prior to the swapping phase. This allows us to compare an extremely high number of tiles without taking much time. Thus, the bulk of the runtime comes from the prior calculations. The Euclidean distance sum of every image at every possible location is calculated and stored in an array.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

Python 3 must be installed in order to run this on your machine. The numpy and cv2 libraries must also be installed.

### Running the Program

Run the program in the command line with:

```
python3 mosaic.py <target image> <directory of tile images>
```

Example:
```
python3 mosaic.py pokemon.jpg /home/auser/mosaic/flowers/
```

You will be prompted for the desired size of the resulting mosaic image. After that, the program will begin.


## Acknowledgments

* Flower image set from https://www.kaggle.com/alxmamaev/flowers-recognition/home
* League of Legends image set from Riot Games

