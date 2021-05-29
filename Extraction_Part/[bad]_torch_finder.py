# Import 
import os
import numpy as np
from numpy.core.fromnumeric import squeeze
from resnet_pytorch import ResNet
from efficientnet_pytorch import EfficientNet
from PIL import Image
import cv2
import operator
import torch
import torchvision

from sklearn.neighbors import NearestNeighbors

# CONST NOUN -------------------------------------------------------------------
PATH_IMG_CLOTH = "/home/kwak/work_space/Finding_System/src/clothes"
PATH_IMG_INPUT = "/home/kwak/work_space/Finding_System/src/extracted_model"

SIZE_CUT = 500
SIZE_CENTER_CROP = 400

# Class Definition -------------------------------------------------------------
class Finding_System():
    def __init__(self, preprocessor, 
                 img_PATH = PATH_IMG_CLOTH, softmax = False, 
                 n_neigh = 5, backbone = 'resnet'):
        '''
        this is Finding System.

        `preprocessor` : torch pre-processor
        `img_PATH` : absolute PATH about input images
        `softmax` : Bool type
        `n_neigh` : N of k-nn model
        `backbone` : `resnet` or `effnet`
        '''
        print('\n Finding System Initialize... ', end='')
        self.backbone = backbone

        if backbone == 'resnet':
            self.model = ResNet.from_pretrained("resnet50")
        elif backbone == 'effnet':
            self.model = EfficientNet.from_pretrained('efficientnet-b0')

        self.search_name = []
        self.search_feature = []

        # TODO : Make Feature List
        for img_name in os.listdir(img_PATH):
            PIL_img = Image.open(os.path.join(img_PATH, img_name))

            feature_torch = self.get_feature(PIL_img, preprocessor, softmax = softmax)  # (n, ) tensor
            feature = feature_torch.tolist()                                            # (n, ) list
            
            self.search_feature.append(feature)                                         # (index, n) list
            self.search_name.append(img_name)                                           # (index, 1) list
        
        # TODO : Make Comparison function
        self.n_neigh = n_neigh
        self.knn = NearestNeighbors(n_neigh)
        self.knn.fit(self.search_feature)

        print(' Done ! \n')


    def get_feature(self, PIL_img, preprocessor, softmax=False):
        '''
        Return Feature about input PIL Image.

        `PIL_img` : PIL Type Image
        `preprocessor` : Torch pre-processor
        `softmax` : Bool type
        '''
        img_tensor = preprocessor(PIL_img)      # ( 3, w, h ) tensor
        img_tensor = img_tensor.unsqueeze(0)    # ( 1, 3, w, h ) tensor

        if self.backbone == 'resnet':
            # Feature Extracting -- ResNet ----------------------------------------------
            features = self.model.extract_features(img_tensor)     # (1, n, 1, 1) tensor
            features = features.detach().numpy()                  # (1, n, 1, 1) numpy
            features = np.squeeze(features)                       # (n, ) numpy

        elif self.backbone == 'effnet':
            # Feature Extracting -- EffNet ----------------------------------------------
            features = self.model.extract_features(img_tensor)   # (1, n, 13, 13) tensor
            temp = []
            features = features.detach().numpy()                # (1, n, 13, 13) numpy
            features = np.squeeze(features)                     # (n, 13, 13) numpy
            for row in features:            
                temp.append(np.mean(row))                       # append mean of (13, 13)
            features = np.array(temp)                           # (n, ) numpy
        # ----------------------------------------------------------------------------
        
        feature_torch = torch.from_numpy(features)              # (n, ) tensor

        # SOFTMAX
        if softmax:
            sfmax = torch.nn.Softmax(dim = 0)
            feature_torch = sfmax(feature_torch)
        
        return feature_torch



    def searching_result(self, PIL_img, preprocessor, softmax = False):
        '''
        searching result about input PIL_img.
        output is result.

        `PIL_img` : PIL Type IMG
        `prepcessor` : torch Preprocessor
        `softmax` : Bool type 
        '''
        feature_torch = self.get_feature(PIL_img, preprocessor, softmax = softmax)  # (n, ) tensor
        
        # make List
        # features = feature_torch.tolist()   # (n, ) list

        cos = torch.nn.CosineSimilarity(dim=0, eps=1e-6)
        result_dict = dict()

        for idx in range(100):
            idx_feature_torch = torch.tensor(self.search_feature[idx])  # (n, ) tensor
            output = cos(feature_torch, idx_feature_torch)

            result_dict[self.search_name[idx]] = output.item() * 100

            # print(f"{self.search_name[idx]} = {output}")

        result_dict = sorted(result_dict.items(), key=operator.itemgetter(1), reverse=True)

        # print("\n\n SORT \n\n")
        # for idx in range(100):
        #     print(f"{result_dict[idx]}")
        # exit(1)

        # input = [features]
        # result = self.knn.kneighbors(input, return_distance=False)
        
        text = f"   \n  Result "
        for i in range(5):
            text = text + f"\n    {result_dict[i]}"

        return text


    def searching_test(self, query_feature):
        for idx in range(100):
            feature_torch = torch.tensor(self.search_feature[idx])  # (n, ) tensor
            print(feature_torch.shape)
            exit(1)



preprocess = torchvision.transforms.Compose([

        torchvision.transforms.ToTensor()
    ])

preprocess_input = torchvision.transforms.Compose([
        torchvision.transforms.ToTensor()
    ])

temp = Finding_System(preprocess, img_PATH=PATH_IMG_CLOTH, softmax=False, n_neigh=5, backbone='resnet')

for idx, file in enumerate(os.listdir(PATH_IMG_INPUT)):
    if idx > 5:
        exit(1)
    print(f"\n\n input : {file}")

    input_img = Image.open(os.path.join(PATH_IMG_INPUT, file))
    result = temp.searching_result(input_img, preprocess_input)
    
    print(result)

    

# test
# for case, answer in testcase.items():
#     print(f'\n\n Case {case} Selected ... / Answer is {answer}')

#     index_test = testcase_index[case]
#     input = [LIST_TEST_FEATURE[index_test]]
#     result = knn.kneighbors(input, return_distance=False)

    # print(f"\n Result \
    #         \n    {LIST_FILE_NAME[result[0][0]]}\
    #         \n    {LIST_FILE_NAME[result[0][1]]}\
    #         \n    {LIST_FILE_NAME[result[0][2]]}\
    #         \n    {LIST_FILE_NAME[result[0][3]]}\
    #         \n    {LIST_FILE_NAME[result[0][4]]}\n")

#     if answer in {LIST_FILE_NAME[result[0][0]], LIST_FILE_NAME[result[0][1]], LIST_FILE_NAME[result[0][2]], LIST_FILE_NAME[result[0][3]], LIST_FILE_NAME[result[0][4]]}:
#         print("\n\n ---- OK this is good ---- \n\n")


#     cv_check_list = []
#     for i in result[0]:
#         cv_check_list.append(LIST_FILE_NAME[i])

#     # ------ Third TODO : OpenCV Similarity Check ------
#     img_dict = {}
#     img_hists_dict = {}

#     for img_name in cv_check_list:
#         img_path = os.path.join(PATH_IMG_CLOTH, img_name)
#         img_dict[img_name] = cv2.imread(img_path)
#         img_dict[img_name] = cv2.resize(img_dict[img_name], dsize=(SIZE_CUT, SIZE_CUT), interpolation=cv2.INTER_AREA)
#         bit = int((SIZE_CUT - SIZE_CENTER_CROP)/2)
#         img_dict[img_name] = img_dict[img_name][bit:SIZE_CUT - bit, bit:SIZE_CUT - bit]

#     img_dict['test'] = cv2.imread(f'/home/kwak/work_space/Finding_System/src/clothes/{case}')

#     for i, (name, img) in enumerate(img_dict.items()):

#         # hsv 변환
#         hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
#         # H, S 히스토그램 계산
#         hist = cv2.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])
        
#         # 정규화
#         cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)

#         img_hists_dict[name] = hist

#     query = img_hists_dict['test']

#     methods = {'CORREL':cv2.HISTCMP_CORREL, 'CHISQR':cv2.HISTCMP_CHISQR,
#                'INTERSECT':cv2.HISTCMP_INTERSECT}


#     for j, (name, flag) in enumerate(methods.items()):
#         print('%-10s'%name, end='\n   ')

#         best = 0.0
#         best_name = ""

#         if name in ['CHISQR', 'BHATTACHARYYA']:
#             best = 1000000000.0

#         for i, (filename, hist) in enumerate(img_hists_dict.items()):
            
#             #---④ 각 메서드에 따라 img1과 각 이미지의 히스토그램 비교
#             ret = cv2.compareHist(query, hist, flag)
            
#             if flag == cv2.HISTCMP_INTERSECT: #교차 분석인 경우 
#                 ret = ret/np.sum(query)        #비교대상으로 나누어 1로 정규화
            
#             print("%20s : %7.6f"% (filename , ret * 100), end='\n   ')

#         print()