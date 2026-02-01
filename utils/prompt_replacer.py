"""
Prompt 占位符替换工具模块
智能识别和替换各种格式的占位符
"""


def smart_replace(template: str, text: str, task_type_name: str = "") -> str:
    """
    智能替换各种可能的占位符格式
    
    Args:
        template: 包含占位符的模板字符串
        text: 要插入的实际文本
        task_type_name: 任务类型名称（用于自动修复）
        
    Returns:
        替换后的完整 Prompt
    """
    # 记录原始模板
    original = template
    
    # 尝试各种占位符格式（按优先级排序）
    replacements = [
        # 标准占位符
        ("{{text}}", text),
        ("{text}", text),
        ("{{input}}", text),
        ("{input}", text),
        
        # 中文方括号占位符
        ("[输入评论]", text),
        ("[待分类文本]", text),
        ("[待翻译文本]", text),
        ("[待摘要文本]", text),
        ("[输入文本]", text),
        ("[文本内容]", text),
        ("[用户输入]", text),
        
        # 中文花括号占位符
        ("【输入评论】", text),
        ("【待分类文本】", text),
        ("【待翻译文本】", text),
        ("【待摘要文本】", text),
        ("【输入文本】", text),
        ("【文本内容】", text),
        ("【待处理文本】", text),
        
        # 英文描述性占位符
        ("[INPUT]", text),
        ("[TEXT]", text),
        ("[CONTENT]", text),
        ("{INPUT}", text),
        ("{TEXT}", text),
        
        # 其他常见格式
        ("<text>", text),
        ("<input>", text),
        ("$text", text),
        ("$input", text),
    ]
    
    result = template
    replaced_count = 0
    replaced_placeholders = []
    
    for placeholder, replacement in replacements:
        if placeholder in result:
            old_result = result
            result = result.replace(placeholder, replacement)
            if result != old_result:
                replaced_count += 1
                replaced_placeholders.append(placeholder)
                print(f"   ✅ 替换 '{placeholder}' -> 实际文本")
    
    if replaced_count == 0:
        print(f"   ⚠️ 警告：未找到任何占位符！")
        print(f"   📋 完整模板内容：")
        print(f"   {template}")
        print(f"   💡 提示：请检查模板中使用的占位符格式")
        print(f"   🔧 尝试自动修复：在 Prompt 末尾添加文本插入位置...")
        
        # 根据任务类型添加合适的提示语
        if "分类" in task_type_name:
            result = template + f"\n\n待分类文本：{text}\n\n请分析上述文本并输出分类结果。"
        elif "摘要" in task_type_name:
            result = template + f"\n\n待摘要文本：\n{text}\n\n请根据上述要求生成摘要。"
        elif "翻译" in task_type_name:
            result = template + f"\n\n待翻译文本：\n{text}\n\n请翻译上述文本。"
        else:
            result = template + f"\n\n输入内容：{text}"
        
        print(f"   ✅ 已自动添加文本到 Prompt 末尾（任务类型：{task_type_name}）")
    else:
        print(f"   ✅ 成功替换 {replaced_count} 个占位符: {', '.join(replaced_placeholders)}")
    
    return result
