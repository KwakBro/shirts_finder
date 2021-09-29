# 개요
> 인터넷에선 사진으로 옷을 찾고싶어 하는 사람들이 많습니다.   
> 본 아이디어는 이러한 사람들의 수요에 맞추어 해당 기능을 만들어 보고자 했습니다.   

# 목적
> 이미지가 주어지면 거기서 상의를 구분하고 DB에 속해있는 아이템 중    
> 가장 유사한 아이템을 결과로 출력해주는 시스템(서비스)

# 기능 블록도
> ![image](https://user-images.githubusercontent.com/68212288/135228975-61910840-ec82-4c74-a5a3-a25707f9699e.png)

# 결과물
> ![image](https://user-images.githubusercontent.com/68212288/135229382-8f1d7cb0-fefb-4428-a2aa-ba6762653bb6.png)
> 동작에 문제가 없는 하나의 APP 서비스 입니다.   

# 성능
> ![image](https://user-images.githubusercontent.com/68212288/135229097-d1229fc9-5244-48c2-aba3-15488eaf3192.png)
> `같은 옷`은 대다수의 Testcase 에서 좋은 결과가 나왔으며   
> `유사한 옷`을 찾는 과정에선 색상 특징이 확실한 경우에만 좋은 결과가 나왔습니다.   

# Directory
> ```
> this 
> │    // django server urls 및 function 파일들 
> │
> ├─ Application Part
> │    // APP 구성 부분
> │
> └─ Extraction Part 
>      // 의상 추출 모델 개발 부분
> ```
> 
> __`[django]views.py`__   
> Django 로 서버 생성 후 `views.py` 함수의 개발 내용 ( ___PREVIOUS Ver.___ )   
>    
> __`urls.py`__   
> Django URL 매칭 정규표현식 위해서 냄겨봄 
