from django.http.response import HttpResponseNotAllowed, HttpResponseNotFound
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import json
import base64
import os
import logging
        
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

formatter = logging.Formatter('[ %(asctime)s ] LOG-%(levelname)s ( %(filename)s at Line %(lineno)s ) : %(message)s',
                              '%Y-%m-%d %H:%M:%S')
logger = logging.getLogger("kwak")
logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

file_handler = logging.FileHandler(filename='/home/kwak/work_space/Finding_System/source.log')
file_handler.setFormatter(formatter)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

############################ For function ###############################

# Create your views here.

@method_decorator(csrf_exempt, name='dispatch')
def accept(request):
    if request.method == "POST":

        rand_id = str(random.random())
        logger.info(f'POST received // ID : {rand_id}')

        start_time = time.time()

        input = json.loads(request.body)
        base64_string = input.get('img_base64', None)

        data = base64.b64decode(base64_string)

        """
        String Decoding, Save Image
        """

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
            # TODO : 옷 사진이 아닌 케이스 -------------------------------------------- ** // OK ! 
            logger.info("Can't find shirts in input image ( casting Time : %3.4f sec )" % (time.time() - start_time))
            return JsonResponse(Json_return(FLAG=0, request_ID=rand_id))
        
        ## Check point
        cv2.imwrite(f'/home/kwak/work_space/Finding_System/src/request_result/{rand_id}.jpg', img_item)

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

            # Matchin Edge 가 6 미만이면 솔직히 좋진 못함.
            if curr_count < 6:
                continue

            if max_count < curr_count:
                max_count = curr_count
                file_max = file_name
                img_max = img_base.copy()
                
        if file_max is not None :
            # TODO : Existing Case 

            if max_count >= 20:
                """
                DB 에 YES 라 생각 ------------------------------------ **
                """
                logger.info("perfectly Matched with '%s' ( casting Time : %3.4f sec )" % (file_max, time.time() - start_time))
                result = searching_funcs.searching_with_npimg(img_item)

                return JsonResponse(Json_return(FLAG=1, request_ID=rand_id, 
                                        db_result=file_max, recommands=[result[0][1], result[1][1], result[2][1]]))

            else:
                # Small is best
                s_score, h_score = searching_funcs.calc_score_npimgs(img_item, img_max)
                
                if h_score <= 60 and s_score <= 4.5:
                    """
                    DB 에 YES 라 생각 ------------------------------------ **
                    """
                    logger.info("2nd Matched with '%s' ( casting Time : %3.4f sec )" % (file_max, time.time() - start_time))
                    logger.info(" Same Score : %2.5f // Hash Score : %2.5f // Count : %3d \n" % (s_score, h_score, max_count))

                    result = searching_funcs.searching_with_npimg(img_item)

                    return JsonResponse(Json_return(FLAG=1, request_ID=rand_id, 
                                            db_result=file_max, recommands=[result[0][1], result[1][1], result[2][1]]))

                else:
                    """
                    DB 에 NONE 이라 생각 ---------------------------------- **
                    """
                    logger.info("2nd Matched fail -- recommand start ( casting Time : %3.4f sec )" % (time.time() - start_time))
                    logger.info(" Same Score : %2.5f // Hash Score : %2.5f // Count : %3d \n" % (s_score, h_score, max_count))

                    result = searching_funcs.searching_with_npimg(img_item)

                    return JsonResponse(Json_return(FLAG=2, request_ID=rand_id, recommands=[result[0][1], result[1][1], result[2][1]]))
            
        else:
            """
            DB 에 NONE 이라 생각 ---------------------------------- **
            """
            logger.info("file_max is None -- recommand start ( casting Time : %3.4f sec )" % (time.time() - start_time))

            result = searching_funcs.searching_with_npimg(img_item)

            return JsonResponse(Json_return(FLAG=2, request_ID=rand_id, recommands=[result[0][1], result[1][1], result[2][1]]))

    else: 
        print("GET receive")
        return HttpResponseNotAllowed("this is Rest API for 'POST'")


def Json_return(FLAG, request_ID, db_result=None, recommands=[None, None, None]):
    dict_temp=dict()

    dict_temp['FLAG'] = FLAG
    dict_temp['request_ID'] = request_ID    # Extracted Item 추출위한 ID
    
    if FLAG == 1:
        dict_temp['result'] = db_result     # DB 에 있는 아이템인 경우 추가

    if FLAG in [1, 2]:                      # 입력이 옷인 경우 recommand 추가
        dict_temp['recommand'] = recommands

    return dict_temp


def return_image(request, image_idx):
    link = os.path.join("/home/kwak/work_space/Finding_System/src/clothes", f"shirts-{image_idx}.jpg")

    try:
        image_data = open(link, "rb").read()
    except FileNotFoundError:
        return HttpResponseNotFound("404 Not Found")

    return HttpResponse(image_data, content_type="image/jpg")


def return_test(request, image_idx):
    link = os.path.join("/home/kwak/work_space/Finding_System/src/request_result", f"{image_idx}.jpg")

    try:
        image_data = open(link, "rb").read()
    except FileNotFoundError:
        return HttpResponseNotFound("404 Not Found")

    return HttpResponse(image_data, content_type="image/jpg")