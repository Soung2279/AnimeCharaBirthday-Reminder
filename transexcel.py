import pandas as pd
import json
import re
from datetime import datetime
from collections import defaultdict

def normalize_name(name):
    """标准化角色名，用于匹配图片链接"""
    return name.strip()

def extract_image_links(txt_content):
    """从文本文件中提取图片链接"""
    pattern = r'\[(.*?)\]\((https?://.*?)\)'
    matches = re.findall(pattern, txt_content)
    
    image_map = defaultdict(list)
    for name, url in matches:
        normalized = normalize_name(name)
        image_map[normalized].append(url)
    
    print(f"共提取到 {len(image_map)} 个图片链接")
    return image_map

def find_matching_image(character_name, image_map):
    """根据角色名查找匹配的图片链接"""
    normalized_char = normalize_name(character_name)
    
    # 完全匹配
    if normalized_char in image_map:
        return image_map[normalized_char][0]  # 返回第一个匹配的URL
    
    # 部分匹配（包含关系）
    for img_name, urls in image_map.items():
        if normalized_char in img_name or img_name in normalized_char:
            return urls[0]
    
    # 尝试忽略姓氏匹配
    char_without_surname = ''.join(normalized_char.split('·')[-1].split(' ')[-1].split('_')[-1].split('-')[-1])
    for img_name, urls in image_map.items():
        img_without_surname = ''.join(img_name.split('·')[-1].split(' ')[-1].split('_')[-1].split('-')[-1])
        if char_without_surname == img_without_surname:
            return urls[0]
    
    return None

def excel_to_json_with_logging(file_path, txt_file_path, output_file="characters_final.json"):
    """处理Excel文件并整合图片链接"""
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 开始处理文件: {file_path}")
    
    try:
        # 第一阶段：处理Excel文件
        print("\n=== 第一阶段：处理Excel文件 ===")
        df = pd.read_excel(file_path)
        print(f"成功读取Excel，共发现 {len(df)} 条记录")
        print(f"检测到列名: {list(df.columns)}")
        
        # 数据清洗
        df = df.fillna('')
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
        
        # 转换为字典列表
        records = []
        for idx, row in df.iterrows():
            try:
                # 处理特殊字段（示例处理自推程度）
                push_level = 0
                if '自推程度' in df.columns:
                    push_level = str(row['自推程度']).count('♥') if pd.notna(row['自推程度']) else 0
                
                record = {
                    "image_url": row.get('角色图片', ''),
                    "character_name": row.get('角色名', ''),
                    "alias": row.get('别名', ''),
                    "category": row.get('分类', ''),
                    "source": row.get('来源', ''),
                    "push_level": push_level,
                    "birthday": row.get('生日', '未公布'),
                    "reason": row.get('自推原因', ''),
                    "note": row.get('备注', ''),
                    "wiki_link": row.get('百科链接', '')
                }
                records.append(record)
                print(f"已处理第 {idx+1} 条记录: {row.get('角色名', '')}")
            except Exception as e:
                print(f"处理第 {idx+1} 条记录时出错: {str(e)}")
                continue
        
        # 构建初始JSON
        result = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "source_file": file_path,
                "record_count": len(records)
            },
            "data": records
        }
        
        # 第二阶段：处理图片链接
        print("\n=== 第二阶段：处理图片链接 ===")
        with open(txt_file_path, 'r', encoding='utf-8') as f:
            txt_content = f.read()
        
        image_map = extract_image_links(txt_content)
        
        for item in result['data']:
            character_name = item['character_name']
            matched_url = find_matching_image(character_name, image_map)
            
            if matched_url:
                # 处理URL，确保是PNG格式, 如果你的URL已经时PNG格式了, 请将下行的 +".png" 去掉
                item['image_url'] = matched_url + ".png"
                print(f"为角色 {character_name} 匹配到图片链接: {matched_url}")
            else:
                print(f"未找到匹配图片: {character_name}")
                item['image_url'] = ""
        
        # 保存最终JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 处理完成，结果已保存到 {output_file}")
        print(f"成功处理 {len(records)}/{len(df)} 条记录")
        return True
        
    except Exception as e:
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 处理失败: {str(e)}")
        return False

if __name__ == "__main__":
    excel_to_json_with_logging(
        file_path = "表1.xlsx", 
        txt_file_path = "temp url.txt", 
        output_file = "characters_url.json"
        )