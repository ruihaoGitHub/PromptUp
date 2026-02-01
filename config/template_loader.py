"""
Meta-Prompt 模板加载器
从外部文件加载长文本 Meta-Prompt 模板
"""
import os
from pathlib import Path


def load_meta_prompt(template_file: str, **kwargs) -> str:
    """
    加载 Meta-Prompt 模板并填充变量
    
    Args:
        template_file: 模板文件名 ('generation', 'classification', 'summarization', 'translation', 'search_space')
        **kwargs: 模板变量（如 task_description, labels_str 等）
        
    Returns:
        填充后的 Meta-Prompt 字符串
        
    Raises:
        FileNotFoundError: 如果模板文件不存在
    """
    # 获取模板文件路径
    current_dir = Path(__file__).parent
    template_path = current_dir / "meta_prompts" / f"{template_file}.txt"
    
    if not template_path.exists():
        raise FileNotFoundError(f"Meta-Prompt 模板不存在: {template_path}")
    
    # 读取模板内容
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # 填充变量
    try:
        formatted_prompt = template_content.format(**kwargs)
        return formatted_prompt
    except KeyError as e:
        missing_key = str(e).strip("'")
        raise ValueError(f"Meta-Prompt 模板缺少必需参数: {missing_key}")


def get_generation_meta_prompt(template_name: str, focus_principles: list, 
                               extra_requirements: list, scene_desc: str,
                               optimization_principles: dict) -> str:
    """
    生成任务的 Meta-Prompt
    
    Args:
        template_name: 框架名称（如 CO-STAR）
        focus_principles: 焦点原则列表
        extra_requirements: 额外要求列表
        scene_desc: 场景描述
        optimization_principles: 优化原则字典
        
    Returns:
        填充后的生成任务 Meta-Prompt
    """
    # 构建焦点原则文本
    principles_text = "\n".join([
        f"   - {optimization_principles.get(p, p)}"
        for p in focus_principles
    ])
    
    # 构建额外要求文本
    extra_text = ""
    if extra_requirements:
        extra_text = "\n\n**场景特定要求**：\n" + "\n".join([
            f"   - {req}" for req in extra_requirements
        ])
    
    return load_meta_prompt(
        'generation',
        template_name=template_name,
        principles_text=principles_text,
        extra_text=extra_text,
        scene_desc=scene_desc if scene_desc else "通用场景"
    )


def get_classification_meta_prompt(task_description: str, labels: list[str]) -> str:
    """
    分类任务的 Meta-Prompt
    
    Args:
        task_description: 任务描述
        labels: 标签列表
        
    Returns:
        填充后的分类任务 Meta-Prompt
    """
    labels_str = ', '.join(labels)
    first_label = labels[0] if labels else '标签'
    
    return load_meta_prompt(
        'classification',
        task_description=task_description,
        labels_str=labels_str,
        first_label=first_label
    )


def get_summarization_meta_prompt(task_description: str, source_type: str,
                                  target_audience: str, focus_points: str,
                                  length_constraint: str = None) -> str:
    """
    摘要任务的 Meta-Prompt
    
    Args:
        task_description: 任务描述
        source_type: 源文本类型
        target_audience: 目标受众
        focus_points: 关注点
        length_constraint: 长度限制
        
    Returns:
        填充后的摘要任务 Meta-Prompt
    """
    length_text = f"\n**篇幅限制**：{length_constraint}" if length_constraint else ""
    
    return load_meta_prompt(
        'summarization',
        task_description=task_description,
        source_type=source_type,
        target_audience=target_audience,
        focus_points=focus_points,
        length_text=length_text
    )


def get_translation_meta_prompt(source_lang: str, target_lang: str,
                                domain: str, tone: str,
                                user_glossary: str = "") -> str:
    """
    翻译任务的 Meta-Prompt
    
    Args:
        source_lang: 源语言
        target_lang: 目标语言
        domain: 应用领域
        tone: 期望风格
        user_glossary: 用户术语表
        
    Returns:
        填充后的翻译任务 Meta-Prompt
    """
    glossary_text = ""
    if user_glossary.strip():
        glossary_text = f"""
**用户指定术语表**：
用户强制指定了以下术语对应关系，必须在 Prompt 中创建一个明确的 Glossary Section 来锁定这些翻译：
{user_glossary}
"""
    
    return load_meta_prompt(
        'translation',
        source_lang=source_lang,
        target_lang=target_lang,
        domain=domain,
        tone=tone,
        glossary_text=glossary_text
    )


def get_search_space_meta_prompt() -> str:
    """
    搜索空间生成的 Meta-Prompt
    
    Returns:
        搜索空间生成 Meta-Prompt
    """
    return load_meta_prompt('search_space')
