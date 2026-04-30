import torch
import torch.nn as nn
import torchvision.models as models
from torchvision.models.detection import fasterrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
import numpy as np
from PIL import Image
import cv2
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class ClothingDetectionModel:
    """
    衣物检测与分类模型
    支持检测衣物类型、颜色、材质等属性
    """
    
    def __init__(self, config=None):
        self.config = config or {}
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.detection_model = self._load_detection_model()
        self.classification_models = self._load_classification_models()
        self.color_extractor = ColorExtractor()
        
    def _load_detection_model(self):
        """加载Faster R-CNN模型用于衣物检测"""
        try:
            model = fasterrcnn_resnet50_fpn(pretrained=True)
            
            # 修改分类头以适应衣物类别
            num_classes = len(self.config.get('clothing_classes', [
                '__background__', 'shirt', 'pants', 'jacket', 'shoes', 
                'hat', 'belt', 'socks', 'dress', 'skirt', 'coat', 'tie'
            ]))
            
            in_features = model.roi_heads.box_predictor.cls_score.in_features
            model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
            
            model.to(self.device)
            model.eval()
            
            logger.info(f"衣物检测模型加载成功，支持 {num_classes-1} 种衣物类别")
            return model
            
        except Exception as e:
            logger.error(f"加载检测模型失败: {str(e)}")
            raise
    
    def _load_classification_models(self):
        """加载各类属性分类模型"""
        models_dict = {}
        
        # 款式分类模型
        models_dict['style'] = self._build_classification_model(12)  # 12种款式
        # 材质分类模型
        models_dict['material'] = self._build_classification_model(8)  # 8种材质
        # 季节分类模型
        models_dict['season'] = self._build_classification_model(4)   # 4个季节
        # 场合分类模型
        models_dict['occasion'] = self._build_classification_model(6) # 6种场合
        
        return models_dict
    
    def _build_classification_model(self, num_classes):
        """构建ResNet50分类模型"""
        model = models.resnet50(pretrained=True)
        num_features = model.fc.in_features
        model.fc = nn.Linear(num_features, num_classes)
        model.to(self.device)
        model.eval()
        return model
    
    def detect_clothing(self, image_path: str, confidence_threshold: float = 0.7) -> List[Dict]:
        """
        检测图像中的衣物并提取属性
        
        Args:
            image_path: 图像路径
            confidence_threshold: 置信度阈值
            
        Returns:
            List[Dict]: 检测到的衣物列表，包含各类属性
        """
        try:
            # 预处理图像
            image = Image.open(image_path).convert('RGB')
            image_tensor = self._preprocess_image(image)
            
            # 物体检测
            with torch.no_grad():
                predictions = self.detection_model([image_tensor.to(self.device)])[0]
            
            # 过滤低置信度检测
            keep_indices = predictions['scores'] > confidence_threshold
            boxes = predictions['boxes'][keep_indices].cpu().numpy()
            labels = predictions['labels'][keep_indices].cpu().numpy()
            scores = predictions['scores'][keep_indices].cpu().numpy()
            
            detected_items = []
            
            for i, (box, label, score) in enumerate(zip(boxes, labels, scores)):
                # 裁剪衣物区域
                x1, y1, x2, y2 = map(int, box)
                clothing_crop = image.crop((x1, y1, x2, y2))
                
                # 提取各类属性
                attributes = {
                    'type': self._get_clothing_type(label),
                    'confidence': float(score),
                    'bbox': [x1, y1, x2, y2],
                    'colors': self.color_extractor.extract_dominant_colors(clothing_crop),
                    'style': self._classify_attribute('style', clothing_crop),
                    'material': self._classify_attribute('material', clothing_crop),
                    'season': self._classify_attribute('season', clothing_crop),
                    'occasion': self._classify_attribute('occasion', clothing_crop),
                    'brand': self._detect_brand(clothing_crop)  # 可选的品牌检测
                }
                
                detected_items.append({
                    'id': f'item_{i}',
                    'attributes': attributes,
                    'image_path': image_path
                })
            
            logger.info(f"检测到 {len(detected_items)} 件衣物")
            return detected_items
            
        except Exception as e:
            logger.error(f"衣物检测失败: {str(e)}")
            return []
    
    def _preprocess_image(self, image):
        """预处理图像"""
        from torchvision import transforms
        
        transform = transforms.Compose([
            transforms.Resize(800),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        return transform(image)
    
    def _get_clothing_type(self, label_id):
        """获取衣物类型名称"""
        clothing_classes = self.config.get('clothing_classes', [
            '__background__', 'shirt', 'pants', 'jacket', 'shoes', 
            'hat', 'belt', 'socks', 'dress', 'skirt', 'coat', 'tie'
        ])
        
        if 0 <= label_id < len(clothing_classes):
            return clothing_classes[label_id]
        return 'unknown'
    
    def _classify_attribute(self, attribute_type, image):
        """分类特定属性"""
        model = self.classification_models.get(attribute_type)
        if not model:
            return 'unknown'
        
        # 预处理图像
        image_tensor = self._preprocess_classification_image(image)
        
        # 预测
        with torch.no_grad():
            output = model(image_tensor.to(self.device))
            _, predicted = torch.max(output, 1)
        
        # 获取类别名称
        class_names = self.config.get(f'{attribute_type}_classes', [])
        if 0 <= predicted.item() < len(class_names):
            return class_names[predicted.item()]
        
        return 'unknown'
    
    def _preprocess_classification_image(self, image):
        """预处理分类图像"""
        from torchvision import transforms
        
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        return transform(image).unsqueeze(0)
    
    def _detect_brand(self, image):
        """检测品牌logo（简化版）"""
        # 这里可以集成专门的品牌检测模型
        # 当前简化为返回'unknown'
        return 'unknown'


class ColorExtractor:
    """颜色提取器"""
    
    def __init__(self):
        self.color_names = {
            (255, 0, 0): 'red',
            (0, 255, 0): 'green',
            (0, 0, 255): 'blue',
            (255, 255, 0): 'yellow',
            (255, 0, 255): 'purple',
            (0, 255, 255): 'cyan',
            (128, 128, 128): 'gray',
            (255, 255, 255): 'white',
            (0, 0, 0): 'black',
            (128, 0, 0): 'maroon',
            (0, 128, 0): 'dark_green',
            (0, 0, 128): 'navy'
        }
    
    def extract_dominant_colors(self, image, num_colors=3):
        """
        提取图像中的主要颜色
        
        Args:
            image: PIL Image对象
            num_colors: 要提取的颜色数量
            
        Returns:
            List[Dict]: 颜色列表，包含RGB值和名称
        """
        # 转换为OpenCV格式
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 调整大小以加快处理
        img = cv2.resize(img, (100, 100))
        
        # 重塑为2D数组
        pixels = img.reshape(-1, 3)
        
        # 使用K-means聚类
        pixels = np.float32(pixels)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
        _, labels, centers = cv2.kmeans(pixels, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # 计算每个簇的大小
        counts = np.bincount(labels.flatten())
        
        # 按频率排序
        sorted_indices = np.argsort(counts)[::-1]
        
        dominant_colors = []
        
        for idx in sorted_indices[:min(num_colors, len(centers))]:
            bgr_color = centers[idx]
            rgb_color = [int(bgr_color[2]), int(bgr_color[1]), int(bgr_color[0])]
            percentage = counts[idx] / len(labels) * 100
            
            # 获取颜色名称
            color_name = self._get_color_name(rgb_color)
            
            dominant_colors.append({
                'rgb': rgb_color,
                'name': color_name,
                'percentage': float(percentage)
            })
        
        return dominant_colors
    
    def _get_color_name(self, rgb_color):
        """获取最接近的颜色名称"""
        min_distance = float('inf')
        closest_name = 'unknown'
        
        for color_rgb, name in self.color_names.items():
            distance = sum((a - b) ** 2 for a, b in zip(rgb_color, color_rgb))
            if distance < min_distance:
                min_distance = distance
                closest_name = name
        
        return closest_name


# 示例使用
if __name__ == "__main__":
    # 配置
    config = {
        'clothing_classes': ['__background__', 'shirt', 'pants', 'jacket', 'shoes'],
        'style_classes': ['casual', 'formal', 'sport', 'business', 'street', 'vintage'],
        'material_classes': ['cotton', 'polyester', 'wool', 'leather', 'denim', 'silk'],
        'season_classes': ['spring', 'summer', 'autumn', 'winter'],
        'occasion_classes': ['work', 'party', 'sports', 'casual', 'formal', 'outdoor']
    }
    
    # 初始化模型
    model = ClothingDetectionModel(config)
    
    # 检测衣物
    results = model.detect_clothing('test_image.jpg')
    
    # 打印结果
    for item in results:
        print(f"检测到衣物: {item['attributes']['type']}")
        print(f"  颜色: {item['attributes']['colors']}")
        print(f"  款式: {item['attributes']['style']}")
        print(f"  材质: {item['attributes']['material']}")
        print(f"  适合季节: {item['attributes']['season']}")
        print(f"  适合场合: {item['attributes']['occasion']}")
        print("-" * 50)
