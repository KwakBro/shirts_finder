from PIL import Image
import os.path as osp
import numpy as np
import os
import torch
import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor
import transforms as T
from engine import train_one_epoch, evaluate
import utils

PATH_SRC = '/home/kwak/work_space/Finding_System/src'
PATH_ORIGIN = '/home/kwak/work_space/Finding_System/src/png_img'
PATH_MASK = '/home/kwak/work_space/Finding_System/src/png_mask'

## ---- DATASET ----
class Shirts_Dataset(object):
    def __init__(self, transforms, root=PATH_SRC):
        self.root = root
        self.transforms = transforms
        # 각 폴더에 해당하는 이미지 파일 읽고 정렬
        self.img = list(sorted(os.listdir(PATH_ORIGIN)))
        self.mask = list(sorted(os.listdir(PATH_MASK)))

    def __getitem__(self, idx):
        img_path = osp.join(PATH_ORIGIN, self.mask[idx])
        mask_path = osp.join(PATH_MASK, self.mask[idx])
        
        img = Image.open(img_path).convert('RGB')
        mask = Image.open(mask_path).convert('L')   # Image(w, h)

        mask = np.array(mask)
        mask[mask >= 1] = 1             # Image 이진화

        obj_ids = np.unique(mask)       # Instance 는 1개밖에 없음. 
        obj_ids = obj_ids[1:]           # [1]
        
        masks = mask == obj_ids[:, None, None]  # np.array (1, w, h)

        num_obj = len(obj_ids)
        # Bounding Box 지정
        boxes = []
        for i in range(num_obj):
            pos = np.where(masks[i]) # pos[0] : 행 // pos[1] : 열
            xmin = np.min(pos[1])
            xmax = np.max(pos[1])
            ymin = np.min(pos[0])
            ymax = np.max(pos[0])
            boxes.append([xmin, ymin, xmax, ymax])

        boxes = torch.as_tensor(boxes, dtype=torch.float32)         # torch(1,4)
        label = torch.ones((num_obj,), dtype=torch.int64)           # torch(1,)
        masks = torch.as_tensor(masks, dtype=torch.uint8)           # torch(1,420,240)

        img_id = torch.tensor([idx], dtype=torch.int64)                                     # torch(1,) 
        area = torch.tensor( (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0]) )    # torch(1,)
        iscrowd = torch.zeros((num_obj,), dtype=torch.int64)                                # torch(1,)

        target = {}
        target['boxes'] = boxes
        target['labels'] = label
        target['masks'] = masks
        target['image_id'] = img_id
        target['area'] = area
        target['iscrowd'] = iscrowd

        if self.transforms is not None:
            img, target = self.transforms(img, target)
        
        return img, target

    def __len__(self):
        return len(self.mask)

## ---- Training ----
class Training_Model():
    def __init__(self):
        self.dataset = Shirts_Dataset(transforms=self.get_transform(train=True))
        self.dataset_test = Shirts_Dataset(transforms=self.get_transform(train=False))

        torch.manual_seed(1) 

        self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')

    def train(self, num_epoch=40):
        torch.manual_seed(1)

        # 랜덤한 indices 구성해서 dataset 분할
        indices = torch.randperm(len(self.dataset)).tolist()
        dataset = torch.utils.data.Subset(self.dataset, indices[:])
        dataset_test = torch.utils.data.Subset(self.dataset_test, indices[-10:])

        # Dataset 으로부터 DataLoader 생성
        data_loader = torch.utils.data.DataLoader(
            dataset, batch_size=2, shuffle=True, num_workers=4,
            collate_fn=utils.collate_fn
        )

        data_loader_test = torch.utils.data.DataLoader(
            dataset_test, batch_size=1, shuffle=False, num_workers=4,
            collate_fn=utils.collate_fn
        )

        num_classes = 2 # 배경(0) 과 사람(1)
        model = self.get_instance_segmentation(num_classes)

        # GPU 사용
        model.to(self.device)
        params = [p for p in model.parameters() if p.requires_grad]

        # optimzer 구성
        optimizer = torch.optim.SGD(params, lr=0.005, momentum=0.9, weight_decay=0.0005)

        # learning rate Scheduler 설정
        lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)

        for epoch in range(num_epoch):
            train_one_epoch(model, optimizer, data_loader, self.device, epoch, print_freq=5)
            lr_scheduler.step()
            evaluate(model, data_loader_test, device=self.device)

        # Training End
        print("Training End")

        torch.save(model, 'torch_model.pt')  # 모델 저장
        torch.save(model.state_dict(), 'torch_statedict.pt')   # stateDict 저장

    @staticmethod
    def get_transform(train):
        transforms = []
        transforms.append(T.ToTensor())

        if train:
            transforms.append(T.RandomHorizontalFlip(0.5))  # 0.5 확률로 Flip

        return T.Compose(transforms)

    @staticmethod
    def get_instance_segmentation(num_classes):
        # pre-trained model 불러오기
        model = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=True)

        in_feature = model.roi_heads.box_predictor.cls_score.in_features
        model.roi_heads.box_predictor = FastRCNNPredictor(in_feature, num_classes)

        # mask classifier를 위한 input feature의 차원 얻음.
        in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
        hidden_layer = 256

        # mask predictor 교체
        model.roi_heads.mask_predictor = MaskRCNNPredictor(in_features_mask, hidden_layer, num_classes)

        return model