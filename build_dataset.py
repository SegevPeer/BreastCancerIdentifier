import config
from imutils import paths
import random, shutil, os

processed_images = 0

originalPaths=list(paths.list_images(config.INPUT_DATASET))
random.seed(7)
random.shuffle(originalPaths)

index=int(len(originalPaths)*config.TRAIN_SPLIT)
trainPaths=originalPaths[:index]
testPaths=originalPaths[index:]

index=int(len(trainPaths)*config.VAL_SPLIT)
valPaths=trainPaths[:index]
trainPaths=trainPaths[index:]

datasets=[("training", trainPaths, config.TRAIN_PATH),
          ("validation", valPaths, config.VAL_PATH),
          ("testing", testPaths, config.TEST_PATH)
]

for (setType, originalPaths, basePath) in datasets:
        print(f'Building {setType} set')

        if not os.path.exists(basePath):
                print(f'Building directory {config.BASE_PATH}')
                os.makedirs(basePath)

        for path in originalPaths:
                file=path.split(os.path.sep)[-1]
                label=file[-5:-4]

                labelPath=os.path.sep.join([basePath,label])
                if not os.path.exists(labelPath):
                        print(f'Building directory {labelPath}')
                        os.makedirs(labelPath)

                newPath=os.path.sep.join([labelPath, file])
                shutil.copy2(path, newPath)
                processed_images += 1
                if processed_images % 1000 == 0:  # Print progress every 10 images (you can adjust this)
                        print(f'Processed {processed_images} images...')
print(f'Processed a total of {processed_images} images.')

