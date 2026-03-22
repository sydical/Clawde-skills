#!/usr/bin/env python3
"""
食材识别脚本
使用 ORB 算法进行图像特征匹配
"""

import cv2
import os
import sys
import argparse
import numpy as np
from pathlib import Path

# 素材库目录
INGREDIENTS_DIR = Path(__file__).parent / "ingredients"
INGREDIENTS_DIR.mkdir(exist_ok=True)

def extract_features(image_path):
    """提取图像 ORB 特征"""
    img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None, None
    
    # 调整图像大小以加快处理速度
    img = cv2.resize(img, (800, 600))
    
    # 创建 ORB 检测器
    orb = cv2.ORB_create(nfeatures=1000)
    keypoints, descriptors = orb.detectAndCompute(img, None)
    
    return keypoints, descriptors

def match_features(query_desc, train_desc):
    """匹配特征点"""
    if query_desc is None or train_desc is None:
        return []
    
    # 创建 BFMatcher
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
    
    try:
        matches = bf.knnMatch(query_desc, train_desc, k=2)
        
        # 应用 Lowe's ratio test
        good_matches = []
        for m_n in matches:
            if len(m_n) == 2:
                m, n = m_n
                if m.distance < 0.75 * n.distance:
                    good_matches.append(m)
        
        return good_matches
    except:
        return []

def recognize_ingredient(query_path, threshold=90):
    """识别食材"""
    # 提取查询图像特征
    query_kp, query_desc = extract_features(query_path)
    if query_desc is None:
        return None, "无法读取图片"
    
    # 对比素材库中的所有图片
    best_match = None
    best_score = 0
    best_name = None
    
    for img_file in INGREDIENTS_DIR.glob("*"):
        if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            name = img_file.stem
            
            train_kp, train_desc = extract_features(img_file)
            if train_desc is None:
                continue
            
            matches = match_features(query_desc, train_desc)
            score = len(matches)
            
            if score > best_score:
                best_score = score
                best_name = name
    
    if best_score >= threshold:
        return best_name, f"识别成功！食材: {best_name} (匹配度: {best_score})"
    else:
        return None, f"未找到相似食材（最高匹配度: {best_score}）"

def add_ingredient(name, image_path):
    """添加食材到素材库"""
    # 检查图片是否存在
    img = cv2.imread(str(image_path))
    if img is None:
        return False, "无法读取图片"
    
    # 保存到素材库
    ext = Path(image_path).suffix.lower()
    save_path = INGREDIENTS_DIR / f"{name}{ext}"
    
    # 如果已存在同名文件，添加数字后缀
    counter = 1
    while save_path.exists():
        save_path = INGREDIENTS_DIR / f"{name}_{counter}{ext}"
        counter += 1
    
    cv2.imwrite(str(save_path), img)
    return True, f"已添加食材: {name} -> {save_path}"

def list_ingredients():
    """列出素材库中的所有食材"""
    ingredients = []
    for img_file in INGREDIENTS_DIR.glob("*"):
        if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            ingredients.append(img_file.stem)
    return ingredients

def main():
    parser = argparse.ArgumentParser(description="食材识别工具")
    parser.add_argument("--query", type=str, help="查询图片路径")
    parser.add_argument("--add", type=str, help="添加食材名称（需要配合图片路径）")
    parser.add_argument("--image", type=str, help="图片路径（配合 --add 使用）")
    parser.add_argument("--list", action="store_true", help="列出所有食材")
    parser.add_argument("--threshold", type=int, default=90, help="匹配阈值")
    
    args = parser.parse_args()
    
    # 列出所有食材
    if args.list:
        ingredients = list_ingredients()
        if ingredients:
            print("素材库中的食材:")
            for ing in ingredients:
                print(f"  - {ing}")
        else:
            print("素材库为空，请先添加食材！")
        return
    
    # 识别食材
    if args.query:
        result, message = recognize_ingredient(args.query, args.threshold)
        print(message)
        if result:
            print(f"RESULT:{result}")
        else:
            print("RESULT:NOT_FOUND")
        return
    
    # 添加食材
    if args.add and args.image:
        success, message = add_ingredient(args.add, args.image)
        print(message)
        return
    
    # 显示帮助
    parser.print_help()
    print("\n示例:")
    print("  识别: python3 recognize.py --query /path/to/image.jpg")
    print("  添加: python3 recognize.py --add 番茄 --image /path/to/tomato.jpg")
    print("  列表: python3 recognize.py --list")

if __name__ == "__main__":
    main()
