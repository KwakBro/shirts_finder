# Extraction Part! ( NEED TRAINING )
__`torch_Extraction.py`__  
> ```
> extraction_model = Extraction_Model(model_savepoint_path='/home/kwak/work_space/Finding_System/torch_save.pt',
>                                     model_state_path='/home/kwak/work_space/Finding_System/torch_state_dict.pt')
>
> img = Image.open('/home/kwak/work_space/Finding_System/src/png_img/17.png').convert('RGB')
> result_pic = extraction_model.get_shirts_pic(img)
> cv2.imwrite('result.jpg', result_pic)
> ```
> __Input__ : `PIL.Image` type 이미지 ( 3, w, h )   
> __Output__ : `CV2 ndarray` type 이미지 ( w, h, 3 )   
   
__`torch_Training.py`__
> ```
> train_class = Training_Model()
> train_class.train( )
> ```
> __Output__ : `Torch Savepoint` File 및 `Torch State dictionary` File   
> 이미지 및 세부사항 변경은 Class 수정하기.   
> [Make Training Set](https://github.com/KwakBro/AI-ML/tree/master/COCO_Creator)
>    
> ```  
> src
>  ├─ clothes   
>  │     ├─ shirts-1.jpg   
>  │     └─ shirts-2.jpg   
>  │         ...   
>  └─ masks   
>        ├─ shirts-1.jpg   
>        └─ shirts-2.jpg   
>            ...   
> ```
# 참고 문헌 및 코드 출처
[PyTorch공식 문서](https://tutorials.pytorch.kr/intermediate/torchvision_tutorial.html)
