"""
JSON 解析工具模块
处理 LLM 返回的各种格式（JSON、Markdown）
"""
import json
import re


def check_unescaped_braces(template: str, template_name: str = "模板") -> None:
    """
    检查模板字符串中是否存在未转义的花括号（会导致 format_messages KeyError）
    
    Args:
        template: 要检查的模板字符串
        template_name: 模板名称（用于错误提示）
    
    Raises:
        ValueError: 如果检测到可疑的未转义花括号
    """
    # 检测单个花括号（可能是未转义的）
    # 排除已经转义的 {{ 和 }}，以及合法的占位符如 {scene_desc}
    
    # 查找所有花括号
    single_open = re.findall(r'(?<!\{)\{(?!\{)', template)
    
    # 查找合法的占位符（如 {scene_desc}, {template_name} 等）
    valid_placeholders = re.findall(r'\{[a-zA-Z_][a-zA-Z0-9_]*\}', template)
    
    # 如果单花括号数量不等于合法占位符数量，说明有问题
    suspicious_count = len(single_open) - len(valid_placeholders)
    
    if suspicious_count > 0:
        print(f"⚠️ 警告：{template_name} 中检测到 {suspicious_count} 个可疑的未转义花括号")
        print("   这可能会导致 format_messages() 时出现 KeyError")
        print(f"   合法占位符: {valid_placeholders}")
        print("   如果模板中包含示例JSON或其他需要显示花括号的内容，请使用 {{{{ 和 }}}} 进行转义")


def parse_markdown_response(content: str) -> dict:
    """
    解析Markdown格式的响应（当模型返回 **字段名**: 而不是JSON时）
    
    Args:
        content: Markdown格式的响应
        
    Returns:
        解析后的字典
    """
    print("🔍 尝试从Markdown格式中提取字段...")
    
    result = {}
    
    # 提取 thinking_process
    thinking_match = re.search(r'\*\*thinking_process\*\*[：:]\s*(.*?)(?=\n\*\*|$)', content, re.DOTALL)
    if thinking_match:
        result['thinking_process'] = thinking_match.group(1).strip()
    
    # 提取 improved_prompt
    improved_match = re.search(r'\*\*improved_prompt\*\*[：:]\s*(.*?)(?=\n\*\*|$)', content, re.DOTALL)
    if improved_match:
        result['improved_prompt'] = improved_match.group(1).strip()
    
    # 提取 enhancement_techniques（列表形式）
    techniques_match = re.search(r'\*\*enhancement_techniques\*\*[：:]\s*(.*?)(?=\n\*\*|$)', content, re.DOTALL)
    if techniques_match:
        techniques_text = techniques_match.group(1).strip()
        # 解析列表项（以 - 开头）
        techniques = re.findall(r'-\s*([^\n]+)', techniques_text)
        if techniques:
            # 清理每个技术项，去除括号中的英文说明
            result['enhancement_techniques'] = [re.sub(r'\s*（.*?）|\s*\(.*?\)', '', t).strip() for t in techniques]
        else:
            # 如果没有列表项，尝试按逗号分割
            result['enhancement_techniques'] = [t.strip() for t in techniques_text.split(',') if t.strip()]
    
    # 提取 keywords_added（列表形式）
    keywords_match = re.search(r'\*\*keywords_added\*\*[：:]\s*(.*?)(?=\n\*\*|$)', content, re.DOTALL)
    if keywords_match:
        keywords_text = keywords_match.group(1).strip()
        keywords = re.findall(r'-\s*([^\n]+)', keywords_text)
        if keywords:
            result['keywords_added'] = [k.strip() for k in keywords]
        else:
            result['keywords_added'] = [k.strip() for k in keywords_text.split(',') if k.strip()]
    
    # 提取 structure_applied
    structure_match = re.search(r'\*\*structure_applied\*\*[：:]\s*([^\n]+)', content)
    if structure_match:
        result['structure_applied'] = structure_match.group(1).strip()
    
    # 设置默认值（如果某些字段缺失）
    if 'thinking_process' not in result:
        result['thinking_process'] = "优化过程分析"
    if 'improved_prompt' not in result:
        result['improved_prompt'] = ""
    if 'enhancement_techniques' not in result:
        result['enhancement_techniques'] = []
    if 'keywords_added' not in result:
        result['keywords_added'] = []
    if 'structure_applied' not in result:
        result['structure_applied'] = "通用框架"
    
    print(f"✅ 从Markdown中提取了 {len(result)} 个字段")
    return result


def safe_json_loads(content: str) -> dict:
    """
    安全地解析JSON字符串，处理控制字符和Markdown格式问题
    
    Args:
        content: JSON字符串或Markdown格式文本
        
    Returns:
        解析后的字典
        
    Raises:
        JSONDecodeError: 如果所有尝试都失败
    """
    # 首先检测是否是Markdown格式（包含 **字段名**: 或 **字段名**： 的模式）
    if '**thinking_process**' in content or '**improved_prompt**' in content:
        print("🔍 检测到Markdown格式响应，优先尝试Markdown解析...")
        try:
            result = parse_markdown_response(content)
            if result.get('improved_prompt'):
                print("✅ Markdown格式解析成功")
                return result
        except Exception as e:
            print(f"⚠️ Markdown解析失败: {str(e)}")
    
    try:
        # 尝试直接解析
        return json.loads(content)
    except json.JSONDecodeError as json_err:
        print(f"⚠️ JSON解析失败: {str(json_err)}")
        
        # 尝试使用 strict=False 参数（允许某些控制字符）
        try:
            result = json.loads(content, strict=False)
            print("✅ 使用 strict=False 解析成功")
            return result
        except:
            pass
        
        # 尝试手动清理控制字符
        try:
            print("⚠️ 尝试手动清理JSON内容")
            # 替换未转义的控制字符
            cleaned_content = content.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            result = json.loads(cleaned_content)
            print("✅ 清理后解析成功")
            return result
        except:
            pass
        
        # 如果上面都失败了，尝试更激进的清理
        try:
            print("⚠️ 尝试使用正则表达式清理")
            # 移除所有ASCII控制字符，除了空格、换行、制表符（JSON结构需要）
            cleaned_content = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', content)
            result = json.loads(cleaned_content)
            print("✅ 正则清理后解析成功")
            return result
        except Exception:
            print("❌ 所有JSON解析尝试均失败")
            print(f"原始内容前500字符: {content[:500]}")
            raise json_err  # 抛出原始错误
