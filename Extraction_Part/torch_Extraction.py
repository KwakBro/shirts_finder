from PIL import Image
import numpy as np
import torch
import cv2
import transforms as T
import time

# ---- Training Main ----
class Extraction_Model():
    def __init__(self, model_savepoint_path, model_state_path, cuda=True):
        if cuda:
            self.device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        else:
            self.device = torch.device('cpu')
        
        self.model = torch.load(model_savepoint_path)
        self.model.load_state_dict(torch.load(model_state_path))

        self.model.to(self.device)
        self.model.eval()

        self.transform = Extraction_Model.get_transform(train=False)

    def get_shirts_pic(self, PIL_img, image_save=False):
        torch.cuda.empty_cache()
        size_w, size_h = PIL_img.size

        if (size_w > 600) or (size_h > 600):
            split_bit = max(int(size_w / 600), int(size_h / 600))
            PIL_img = PIL_img.resize((size_w//split_bit , size_h//split_bit), Image.ANTIALIAS)

        img, _ = self.transform(PIL_img, None)

        with torch.no_grad():
            prediction = self.model([img.to(self.device)])

        try:
            # Error Case
            if torch.max(prediction[0]['scores'].cpu()).item() < 0.85:
                print("BAD CASE")
                return None
                
        except(RuntimeError):
            return None

        np_img = img.mul(255).byte().cpu().numpy()          # ndarray(3, w, h)

        # TODO : Mask Pre-Processing ----------------------------------------------------------------
        # `mask` : `Numpy` Object ( 0 or 1 )
        OUT_THRESHOLD = 100
        IN_THRESHOLD = 250
        
        mask_map = prediction[0]['masks'][0,0].mul(255).byte().cpu().numpy()      # ndarray(w, h)

        out_mask = np.where(mask_map > OUT_THRESHOLD, 1, 0)
        in_mask = np.where(mask_map > IN_THRESHOLD, 1, 0)
    
        # TODO : Accepting Mask Test ----------------------------------------------------------------
        # `masked_img` : `Numpy` Object ( 0 ~ 255 )
        if image_save:
            masked_img = np.copy(np_img)
            masked_img[0] = out_mask * masked_img[0]
            masked_img[1] = out_mask * masked_img[1]
            masked_img[2] = out_mask * masked_img[2]

            in_masked_img = np.copy(np_img)
            in_masked_img[0] = in_mask * in_masked_img[0]
            in_masked_img[1] = in_mask * in_masked_img[1]
            in_masked_img[2] = in_mask * in_masked_img[2]

            temp = Image.fromarray(np.transpose(masked_img, (1, 2, 0))) 
            temp.save("[DEBUG]_out_mask.jpg", 'JPEG')
            temp = Image.fromarray(np.transpose(in_masked_img, (1, 2, 0))) 
            temp.save("[DEBUG]_in_mask.jpg", 'JPEG')

        # TODO : Grab-cut Optimizing ----------------------------------------------------------------
        np_img = np.transpose(np_img, (1, 2, 0))                # ndarray(w, h, 3)  , 원본 Img
        np_img = cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB)        # PIL.Image to CV2 image

        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        grab_cut_mask = np.zeros(np_img.shape[:2], np.uint8)

        ymin = np.min(np.where(out_mask == 1)[0])
        ymax = np.max(np.where(out_mask == 1)[0])
        xmin = np.min(np.where(out_mask == 1)[1])
        xmax = np.max(np.where(out_mask == 1)[1])
        rect = (xmin, ymin, xmax, ymax)

        if image_save:
            cv2.imwrite("[DEBUG]_input.jpg", np_img)

        cv2.grabCut(np_img, grab_cut_mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)

        # Grab_cut_mask 는 out mask 범위 밖은 배경 / in mask 범위 안은 전경으로 설정
        grab_cut_mask[in_mask == 1] = 1
        grab_cut_mask[out_mask == 0] = 0

        cv2.grabCut(np_img, grab_cut_mask, None, bgd_model, fgd_model, 1, cv2.GC_INIT_WITH_MASK)

        grab_cut_mask2 = np.where((grab_cut_mask == 2) | (grab_cut_mask == 0), 0, 1).astype('uint8')

        np_img = cv2.bitwise_not(np_img)
        np_img = np_img * grab_cut_mask2[:, :, np.newaxis]
        np_img = cv2.bitwise_not(np_img)
     
        if image_save:
            cv2.imwrite("result_item.jpg", np_img[ymin:ymax, xmin:xmax])

        torch.cuda.empty_cache()
        
        return np_img[ymin:ymax, xmin:xmax]     # ndarray ( w, h, 3)

    @staticmethod
    def get_transform(train):
        transforms = []
        transforms.append(T.ToTensor())
        if train:
            transforms.append(T.RandomHorizontalFlip(0.5))  # 0.5 확률로 Flip
        return T.Compose(transforms)