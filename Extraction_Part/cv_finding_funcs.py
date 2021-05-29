import cv2
import imagehash
from PIL import Image
import numpy as np
import os
import csv

INDEX_PATH = "/home/kwak/work_space/Finding_System/index.csv"
DATASET_PATH = "/home/kwak/work_space/Finding_System/src/clothes"
BIN_SET = (8, 12, 3)

class ColorDescriptor:
    def __init__(self, bins):
        self.bins = bins
    
    def describe(self, image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        features = []

        (h, w) = image.shape[:2]
        (cX, cY) = (int(w * 0.5), int(h * 0.5))

        segments = [(0, cX, 0, cY), (cX, w, 0, cY), (cX, w, cY, h), (0, cX, cY, h)]

        # HSV 히스토그램 1234번 생성
        for (startX, endX, startY, endY) in segments:
            cornerMask = np.zeros(image.shape[:2], dtype="uint8")
            cv2.rectangle(cornerMask, (startX, startY), (endX, endY), 255, -1)
            
            hist = self.histogram(image, cornerMask)
            
            # 요소 Expending
            features.extend(hist)
        
        # Hash Key 생성
        return features

    def histogram(self, image, mask):
        hist = cv2.calcHist([image], [0, 1, 2], mask, self.bins,
                            [0, 180, 0, 256, 0, 256])
        
        # 지역적 특징 추가를 위해 normalize.
        hist = cv2.normalize(hist, hist).flatten()

        return hist


class Searcher:
    def __init__(self, indexPath):
        self.indexPath = indexPath
    
    def _search(self, queryFeatures, limit = 10):
        result = {}
        with open(self.indexPath) as f:
            reader = csv.reader(f)

            for row in reader:
                # Index 에서 값은 idx 1 부터.
                features = [float(x) for x in row[1:]]
                d = self._chi2_distance(features, queryFeatures)

                result[row[0]] = d
            
            f.close()
        
        result = sorted([(v, k) for (k, v) in result.items()])

        return result[:limit]
    
    def _chi2_distance(self, histA, histB, eps = 1e-10):
        d = 0.5 * np.sum( [ ( ( a - b ) ** 2 ) / ( a + b + eps ) for (a, b) in zip(histA, histB) ] )

        return d


class Funcs(ColorDescriptor, Searcher):
    def __init__(self, bin_set=BIN_SET, index_path=INDEX_PATH, dataset_path = DATASET_PATH):
        ColorDescriptor.__init__(self, bin_set)
        Searcher.__init__(self, index_path)

        if not os.path.isfile(index_path):
            output = open(index_path, "w")

            for image_file_name in os.listdir(dataset_path):
                Path = os.path.join(dataset_path, image_file_name)
                
                imageID = image_file_name
                image = cv2.imread(Path)

                features = self.describe(image)

                features = [str(f) for f in features]
                output.write("%s,%s\n" % (imageID, ",".join(features)))

            output.close()

    def searching_with_npimg(self, query_img):
        query_feature = self.describe(query_img)
        result = self._search(query_feature, limit = 5)

        cv2.imwrite("query.png", query_img)

        return result

    def calc_score_npimgs(self, img_1, img_2):
        feature_1 = self.describe(img_1)
        feature_2 = self.describe(img_2)

        score = self._chi2_distance(feature_1, feature_2)

        return score

    @staticmethod
    def calc_hash(img1, img2, mode):
        """
        input 은 무조건 cv2 (ndarray 형식)
        
        `mode` : [ 'phash': Perceptual hashing,
                        'dhash': Difference hashing,
                        'colorhash' : Color hashing,
                        'average_hash' : Average Hashing ]
        """
        mode_dict = { 'phash': imagehash.phash,'dhash': imagehash.dhash,
                    'colorhash' : imagehash.colorhash,'average_hash' : imagehash.average_hash }
        
        hash_1 = mode_dict[mode](Image.fromarray(img1), 20)
        hash_2 = mode_dict[mode](Image.fromarray(img2), 20)

        return hash_1 - hash_2
