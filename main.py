import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv

# 1. 加载配置
load_dotenv()

# 2. 初始化客户端
client = OpenAI(
    api_key=os.getenv("AI_API_KEY"),
    base_url=os.getenv("AI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
    timeout=120.0  # 增加超时时间到 2 分钟
)

# 3. 定义超级 Prompt
SYSTEM_PROMPT = """
你是一位精通记忆心理学和考试命题的专家。你的任务是将用户提供的文本转化为"高强度段落填空专项训练卷"。

【核心目标】
帮助学生进行三天后的考试复习，通过高密度、多维度的填空训练，实现深度理解和牢固记忆。

【输出结构要求】
请严格按照以下逻辑组织内容，并转化为 JSON 数组（每个元素是一张 Anki 卡片）：
1. 章节 (Chapter) -> 对应大标题
2. 模块 (Module) -> 对应具体知识点
3. 训练组 (Training Set) -> 包含多种考法

【具体考法要求】（必须混合包含以下四种，且明确标注）
1. 概念填空：针对核心定义的精准挖空。
2. 同义填空：用不同的表述方式考察同一概念。
3. 反向填空：使用"不是"、"除了"、"错误"、"不属于"等否定词进行考察。
4. 论述填空：针对长难句、逻辑推导过程、因果关系进行挖空。

【格式规范 - 极其重要】
- 每张卡片 (JSON object) 代表一个"训练段落"。
- `type`: 固定为 "cloze"。
- `front`: 
    - 必须是**段落形式**，不要只给一句话。
    - 【强制数量】：每个段落必须包含 3 到 5 个挖空！不要只挖一个词。
    - 使用 Anki 语法 `{{c1::答案}}`, `{{c2::答案}}` 等。注意：每个挖空必须使用**不同的编号**（c1, c2, c3...），这样 Anki 才能逐个考察。
    - 在 `front` 的开头加上小标题，格式为：`### [章节] [模块] - [训练类型]`，并用 `<br>` 换行。
    - 不同句子之间用 `<br><br>` 分隔。
- `back`: 填写完整原文，或者该段落的详细解析/答案列表。

【示例参考】
用户输入：侦查是指公安机关和人民检察院为了查明案情...
你的输出 (front 字段内容):
### 第一章 侦查原理 - 模块一：侦查概念 - 训练1（概念+段落）<br>
在刑事诉讼理论中，所谓"侦查"，是指 {{c1::公安机关}} 和 {{c2::人民检察院}} 为了查明 {{c3::案情}}、收集 {{c4::证据}}，依法对与案件有关的人或事采取工作措施和强制措施的活动。<br><br>
侦查的核心目的在于 {{c1::收集证据}}、{{c2::查明真相}} 和 {{c3::打击犯罪}}。

【严格约束】
- 不要遗漏任何知识点。
- 每个重要概念至少要出现在 2 张不同的卡片中（重复考察）。
- 填空内容越详细越好，可以挖短语或短句。
- 输出必须是纯 JSON 数组，不要包含 Markdown 代码块标记。
- 只返回 JSON，不要任何解释文字。
"""

def generate_cards(text: str, mode: str = "cloze") -> list:
    """调用 AI 生成卡片，支持模式选择，带重试机制"""
    
    # 截断文本（避免 token 超限）
    if len(text) > 4000:
        text = text[:4000] + "\n...（内容过长，已截断）"
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"🔄 第 {attempt + 1} 次尝试生成卡片...")
            
            response = client.chat.completions.create(
                model=os.getenv("AI_MODEL", "qwen-turbo"),
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"请为以下文本生成高强度填空训练卷：\n\n{text}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            raw_text = response.choices[0].message.content.strip()
            print(f"✅ AI 返回内容长度: {len(raw_text)} 字符")
            
            # 清理 Markdown 标记
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```", 2)[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:].strip()
            
            # 尝试解析 JSON
            data = json.loads(raw_text)
            
            # 兼容处理：检查返回的数据结构
            if isinstance(data, dict) and "cards" in data:
                cards = data["cards"]
            elif isinstance(data, list):
                cards = data
            elif isinstance(data, dict):
                cards = [data]
            else:
                raise ValueError(f"未知的 JSON 结构: {type(data)}")
            
            print(f"✨ 成功解析 {len(cards)} 张卡片")
            return cards
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败（第 {attempt + 1} 次）: {e}")
            if attempt == max_retries - 1:
                # 最后一次尝试失败，返回空列表
                return []
            time.sleep(2)  # 等待 2 秒后重试
            
        except Exception as e:
            print(f"❌ 调用失败（第 {attempt + 1} 次）: {e}")
            if attempt == max_retries - 1:
                return []
            time.sleep(2)
    
    return []

if __name__ == "__main__":
    TEST_TEXT = """侦查是指公安机关和人民检察院为了查明案情、收集证据，依法对与案件有关的场所、物品、人身采取工作措施和强制措施的活动。侦查的核心目的在于收集证据、查明真相。"""
    print("🔄 正在生成高强度训练卷...")
    cards = generate_cards(TEST_TEXT, mode="cloze")
    if cards:
        print(f"✅ 成功生成 {len(cards)} 组训练！")
        print(cards[0].get('front')[:200] + "...")
    else:
        print("❌ 未生成任何卡片")