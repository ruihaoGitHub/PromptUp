"""
搜索空间生成器
用于自动生成优化搜索的参数空间
"""
import time
import json
from langchain_core.prompts import ChatPromptTemplate
from config.models import SearchSpace
from config.template_loader import get_search_space_meta_prompt


class SearchSpaceGenerator:
    """搜索空间生成器"""
    
    def __init__(self, llm, provider: str):
        """
        初始化生成器
        
        Args:
            llm: LangChain LLM 实例
            provider: API 提供商
        """
        self.llm = llm
        self.provider = provider
    
    def generate(self, task_description: str, task_type: str = "classification", **kwargs) -> SearchSpace:
        """
        让 LLM 自动分析任务，生成可供搜索的变量池
        
        Args:
            task_description: 任务描述
            task_type: 任务类型 (classification/summarization/translation)
            **kwargs: 额外的任务配置信息
                - labels: 分类任务的标签列表
                - source_type: 摘要任务的源文本类型
                - target_audience: 摘要任务的目标受众
                - focus_points: 摘要任务的核心关注点
                - source_lang: 翻译任务的源语言
                - target_lang: 翻译任务的目标语言
                - domain: 翻译任务的应用领域
                - tone: 翻译任务的期望风格
            
        Returns:
            SearchSpace 对象，包含 roles, styles, techniques
        """
        print(f"\n{'='*60}")
        print(f"🧠 生成搜索空间")
        print(f"{'='*60}")
        print(f"任务类型: {task_type}")
        print(f"任务描述: {task_description}")
        print(f"{'='*60}\n")
        
        # 使用外部模板加载 Meta-Prompt
        system_prompt = get_search_space_meta_prompt()
        
        # 构建详细的任务上下文
        context_info = f"""
任务类型：{task_type}
任务描述：{task_description}
"""
        
        # 根据任务类型添加特定的上下文信息
        if task_type == "classification" and kwargs.get('labels'):
            context_info += f"""
分类标签：{', '.join(kwargs['labels'])}
"""
        elif task_type == "summarization":
            if kwargs.get('source_type'):
                context_info += f"""
源文本类型：{kwargs['source_type']}
"""
            if kwargs.get('target_audience'):
                context_info += f"""
目标受众：{kwargs['target_audience']}
"""
            if kwargs.get('focus_points'):
                context_info += f"""
核心关注点：{kwargs['focus_points']}
"""
        elif task_type == "translation":
            if kwargs.get('source_lang') and kwargs.get('target_lang'):
                context_info += f"""
翻译方向：{kwargs['source_lang']} → {kwargs['target_lang']}
"""
            if kwargs.get('domain'):
                context_info += f"""
应用领域：{kwargs['domain']}
"""
            if kwargs.get('tone'):
                context_info += f"""
期望风格：{kwargs['tone']}
"""
        
        user_prompt = f"""
{context_info}

请为这个任务设计：
1. 5个不同的角色定位（从保守到创新，覆盖不同专业背景）
2. 5种不同的回答风格/语气
3. 3种不同的提示工程技巧或指令模式

确保输出纯 JSON 格式。
"""
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", user_prompt)
        ])
        
        try:
            # 调用 LLM
            print("📡 调用 LLM 生成搜索空间...")
            messages = prompt_template.format_messages(task_type=task_type, task_description=task_description)
            response = self.llm.invoke(messages)
            
            time.sleep(0.5)  # API 调用延迟，避免频率过快
            
            print(f"✅ LLM 响应成功")
            print(f"原始响应长度: {len(response.content)} 字符")
            
            # 解析 JSON
            content = response.content.strip()
            print(f"\n🔍 解析 JSON 响应...")
            print(f"原始内容前100字符: {content[:100]}...")
            
            # 移除可能的 markdown 代码块标记
            if content.startswith("```json"):
                content = content[7:]
                print("  移除了 ```json 标记")
            if content.startswith("```"):
                content = content[3:]
                print("  移除了 ``` 标记")
            if content.endswith("```"):
                content = content[:-3]
                print("  移除了尾部 ``` 标记")
            content = content.strip()
            
            # 提取 JSON 部分（从第一个 { 到最后一个 }）
            try:
                start_idx = content.index('{')
                end_idx = content.rindex('}') + 1
                content = content[start_idx:end_idx]
                print(f"  提取了纯 JSON 内容（从第 {start_idx} 到第 {end_idx} 字符）")
            except ValueError:
                print("  ⚠️ 未找到完整的 JSON 对象，尝试直接解析")
            
            print(f"清理后内容前100字符: {content[:100]}...")
            
            data = json.loads(content)
            print(f"✅ JSON 解析成功")
            print(f"  - roles: {len(data.get('roles', []))} 个")
            print(f"  - styles: {len(data.get('styles', []))} 个")
            print(f"  - techniques: {len(data.get('techniques', []))} 个")
            
            # 处理 LLM 可能返回对象数组的情况
            def extract_names(items):
                """提取字符串或对象数组中的名称"""
                if not items:
                    return []
                result = []
                for item in items:
                    if isinstance(item, str):
                        result.append(item)
                    elif isinstance(item, dict) and 'name' in item:
                        result.append(item['name'])
                        print(f"    提取: {item['name']}")
                return result
            
            # 转换数据格式
            print(f"🔄 处理数据格式...")
            data['roles'] = extract_names(data.get('roles', []))
            data['styles'] = extract_names(data.get('styles', []))
            data['techniques'] = extract_names(data.get('techniques', []))
            
            print(f"  ✅ roles: {data['roles']}")
            print(f"  ✅ styles: {data['styles']}")
            print(f"  ✅ techniques: {data['techniques']}")
            
            result = SearchSpace(**data)
            print(f"\n✅ 搜索空间生成完成！\n")
            return result
            
        except Exception as e:
            print(f"\n❌ 生成搜索空间失败！")
            print(f"错误类型: {type(e).__name__}")
            print(f"错误信息: {e}")
            
            import traceback
            print(f"\n完整错误堆栈：")
            traceback.print_exc()
            
            # 重新抛出异常，让上层处理
            raise RuntimeError(f"搜索空间生成失败: {e}")
