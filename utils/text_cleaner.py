"""
文本清理工具模块
清理 LLM 输出的各种格式问题
"""
import json
import re


def clean_improved_prompt(improved_prompt: str) -> str:
    """
    清理 improved_prompt 字段，确保不包含JSON格式的文本
    处理大模型误将JSON当作优化结果的情况
    
    Args:
        improved_prompt: 原始的 improved_prompt 内容
        
    Returns:
        清理后的纯文本 prompt
    """
    # 去除首尾空白
    cleaned = improved_prompt.strip()
    
    # 检测是否是JSON格式（以 { 开头，} 结尾）
    if cleaned.startswith('{') and cleaned.endswith('}'):
        print("⚠️ 检测到 improved_prompt 是JSON格式，尝试转换为自然语言...")
        
        try:
            # 尝试解析JSON
            json_data = json.loads(cleaned)
            
            # 将JSON转换为自然语言描述
            prompt_parts = []
            
            # 检查常见字段并构建自然语言描述
            if "任务描述" in json_data:
                prompt_parts.append(f"任务：{json_data['任务描述']}")
            
            if "约束条件" in json_data:
                constraints = json_data["约束条件"]
                if isinstance(constraints, dict):
                    prompt_parts.append("\n约束条件：")
                    for key, value in constraints.items():
                        prompt_parts.append(f"- {key}：{value}")
            
            if "输出要求" in json_data:
                output_req = json_data["输出要求"]
                if isinstance(output_req, dict):
                    prompt_parts.append("\n输出要求：")
                    for key, value in output_req.items():
                        if value:  # 如果值非空
                            prompt_parts.append(f"- {key}：{value}")
                        else:
                            prompt_parts.append(f"- {key}")
            
            if "语气风格" in json_data:
                prompt_parts.append(f"\n语气风格：{json_data['语气风格']}")
            
            if "平台" in json_data:
                prompt_parts.append(f"\n目标平台：{json_data['平台']}")
            
            if prompt_parts:
                converted = "\n".join(prompt_parts)
                print(f"✅ 已将JSON格式转换为自然语言（{len(converted)}字符）")
                
                # 添加友好的提示文本
                result = f"""请完成以下任务：

{converted}

请用专业且{json_data.get('语气风格', '友好')}的语气完成这个任务，确保输出符合所有要求。"""
                
                return result
        
        except json.JSONDecodeError:
            print("⚠️ JSON解析失败，保持原样")
            pass
    
    # 检测是否包含大量JSON特征（即使不是完整JSON）
    if cleaned.count('{') > 3 and cleaned.count(':') > 3 and cleaned.count('"') > 6:
        print("⚠️ 检测到类似JSON的结构化文本，但不是完整JSON格式")
        # 保持原样，但添加警告
    
    return cleaned


def clean_classification_output(text: str) -> str:
    """
    清理分类输出，提取真正的标签
    
    Args:
        text: 模型原始输出文本
        
    Returns:
        清理后的标签文本
    """
    text = text.strip()
    
    # 尝试解析JSON格式
    try:
        # 检查是否是JSON格式
        if text.startswith('{') or text.startswith('['):
            data = json.loads(text)
            # 尝试提取label字段
            if isinstance(data, dict):
                if 'label' in data:
                    return str(data['label']).strip()
                if 'category' in data:
                    return str(data['category']).strip()
                if 'result' in data:
                    return str(data['result']).strip()
    except:
        pass
    
    # 移除常见前缀
    text = re.sub(r'^(标签[:：]|分类[:：]|结果[:：]|label[:：]|category[:：])\s*', '', text, flags=re.IGNORECASE)
    
    # 移除引号
    text = text.strip('"\'')
    
    # 只取第一行第一个词
    text = text.split('\n')[0].split()[0] if text else text
    
    return text.strip()
