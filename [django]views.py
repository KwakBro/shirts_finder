from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import json
import base64
import os
        
############################ For Detector ###############################
import sys
import random
import time
import cv2
sys.path.append('/home/kwak/work_space/Finding_System/Extraction_Part')

import torch_Extraction as Extractor
import cv_finding_funcs as Find_func

ITEM_PATH = "/home/kwak/work_space/Finding_System/src/clothes"
item_extractior = Extractor.Extraction_Model(model_savepoint_path='/home/kwak/work_space/Finding_System/Extraction_Part/torch_save.pt',
                                             model_state_path='/home/kwak/work_space/Finding_System/Extraction_Part/torch_state_dict.pt')
img_descripter = cv2.ORB_create()
img_matcher = cv2.BFMatcher(cv2.NORM_HAMMING)
searching_funcs = Find_func.Funcs()

############################ For function ###############################
# Create your views here.
@method_decorator(csrf_exempt, name='dispatch')
def accept(request):
    if request.method == "POST":
        print(" POST start ")
        start_time = time.time()

        input = json.loads(request.body)
        base64_string = input.get('img_base64', None)

        data = base64.b64decode(base64_string)


        """
        String Decoding, Save Image
        """
        rand_id = str(random.random())

        file_path = f'/home/kwak/work_space/Finding_System/src/{rand_id}_input.png'
        with open(file_path, 'wb') as f:
            f.write(data)
        

        """
        Extract Item
        """
        img_input = Extractor.Image.open(file_path).convert('RGB')
        os.remove(file_path)  # 읽었으면 삭제

        img_item = item_extractior.get_shirts_pic(img_input)

        if img_item is None:
            # TODO : 옷 사진이 아닌 케이스 ------------------------------------------------------------- ** // OK ! 
            print("this is not shirts")
            return JsonResponse({
                'FLAG' : 0,
                'temp' : { 'omg' : 1 },
            })
        
        ## Check point
        cv2.imwrite(f'/home/kwak/work_space/Finding_System/src/{rand_id}_result.png', img_item)
        os.remove(f'/home/kwak/work_space/Finding_System/src/{rand_id}_result.png')

        """
        Searching Item
        """
        max_count = 0
        file_max = None
        img_max = None

        # input Item Description 계산
        _, des_input = img_descripter.detectAndCompute(img_item, None)

        for file_name in os.listdir(ITEM_PATH):
            # Data Base 계산
            img_base = cv2.imread( os.path.join(ITEM_PATH, file_name) )
            _, des_base = img_descripter.detectAndCompute(img_base, None)

            # DB item 과의 Matching 계산
            match_result = img_matcher.knnMatch(des_input, des_base, k=2)

            # Matching 다듬기
            good_matches = [first for first,second in match_result if first.distance < second.distance * 0.7]
            curr_count = len(good_matches)

            if max_count < curr_count:
                max_count = curr_count
                file_max = file_name
                img_max = img_base.copy()
                
        if file_max is not None:
            # TODO : Existing Case ------------------------------------------------------------- **
            ret = searching_funcs.calc_score_npimgs(img_item, img_max)

            print(f"\n this item have item {file_max} \n")
            print(" Same Score : %2.5f // Count : %3d \n" % (ret, max_count))
            
        else:
            # TODO : Not Existing Case ------------------------------------------------------------- **
            print("\n this item don't have matched item \n")

            # Get Similar Cloth
            result = searching_funcs.searching_with_npimg(img_item)

            print(result)

        print(" \n  POST end : %3.4f sec" % (time.time() - start_time))
        return HttpResponse("Hello worl21d")

    else: 
        print("GET sended")
        return HttpResponse("Hello world")
