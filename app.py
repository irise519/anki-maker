# -*- coding: utf-8 -*-
import streamlit as st
from pypdf import PdfReader
from docx import Document
import os
import tempfile
import genanki
import time
from main import generate_cards

# ============ 📦 核心导出函数 (保持不变) ============
def export_to_apkg(cards, deck_name="AI_专项训练卷"):
    """将卡片列表打包为 .apkg 文件"""
    
    # 1. 定义填空卡模型 (Cloze Model)
    cloze_model = genanki.Model(
        1607392319,
        'AI_Cloze_Model',
        fields=[{'name': 'Text', 'type': 'CLOZE'}, {'name': 'Extra'}],
        templates=[{
            'name': 'Cloze',
            'qfmt': '{{cloze:Text}}<br><div style="font-size:0.8em;color:#666;margin-top:10px;">{{Extra}}</div>',
            'afmt': '{{cloze:Text}}<hr id="answer"><div class="answer-box">{{Extra}}</div>'
        }],
        css="""
        .card { font-family: "Segoe UI", "PingFang SC", sans-serif; font-size: 19px; line-height: 1.7; color: #1f2937; }
        h3.section-title { background: #EEF2FF; color: #4338CA; padding: 8px 12px; border-radius: 8px; margin: 12px 0 8px; font-size: 0.85em; font-weight: 600; border-left: 4px solid #6366F1; }
        .cloze { color: #2563EB; font-weight: bold; background: #DBEAFE; padding: 2px 6px; border-radius: 5px; }
        .answer-box { text-align: left; background: #F9FAFB; padding: 16px; border-radius: 10px; border-left: 4px solid #10B981; margin-top: 20px; font-size: 0.9em; color: #374151; }
        br { margin-bottom: 6px; }
        """
    )
    
    # 2. 定义翻转卡模型 (Basic Model)
    basic_model = genanki.Model(
        1584563748,
        'AI_Basic_Model',
        fields=[{'name': 'Question'}, {'name': 'Answer'}],
        templates=[{
            'name': 'Card 1',
            'qfmt': '<div style="font-size:1.1em;line-height:1.6;">{{Question}}</div>',
            'afmt': '{{FrontSide}}<hr id="answer"><div class="answer-box" style="margin-top:20px;">{{Answer}}</div>'
        }],
        css="""
        .card { font-family: "Segoe UI", "PingFang SC", sans-serif; font-size: 19px; color: #1f2937; }
        h3.section-title { background: #EEF2FF; color: #4338CA; padding: 8px 12px; border-radius: 8px; margin: 12px 0 8px; font-size: 0.85em; font-weight: 600; border-left: 4px solid #6366F1; }
        .answer-box { text-align: left; background: #F9FAFB; padding: 16px; border-radius: 10px; border-left: 4px solid #10B981; font-size: 0.95em; color: #374151; }
        """
    )
    
    # 3. 创建牌组并添加卡片
    deck = genanki.Deck(1584563749, deck_name)
    for card in cards:
        card_type = card.get('type', 'cloze')
        front = card.get('front', '').replace('### ', '<h3 class="section-title">').replace('**', '')
        back = card.get('back', '').replace('**', '').replace('\n', '<br>')
        
        if card_type == 'cloze':
            note = genanki.Note(model=cloze_model, fields=[front, back])
        else:
            note = genanki.Note(model=basic_model, fields=[front, back])
        deck.add_note(note)
    
    # 4. 导出文件
    tmp_dir = tempfile.gettempdir()
    apkg_path = os.path.join(tmp_dir, f"{deck_name}.apkg")
    genanki.Package(deck).write_to_file(apkg_path)
    return apkg_path

# ============ 🎨 CSS 样式 (含移动端适配) ============
st.markdown("""
<style>
    /* 全局背景 */
    .stApp { background: #F3F4F6; }
    
    /* 主容器 */
    .main-container { 
        background: white; 
        border-radius: 16px; 
        padding: 2rem; 
        box-shadow: 0 4px 24px rgba(0,0,0,0.06); 
        margin: 1rem auto; 
        max-width: 1100px; 
    }
    
    /* 标题 */
    .main-title { 
        font-size: 3.2rem; 
        font-weight: 800; 
        color: #4338CA !important; 
        text-align: center; 
        margin: 1.5rem 0 0.5rem; 
        text-shadow: 2px 2px 8px rgba(67, 56, 202, 0.25); 
    }
    .subtitle { 
        text-align: center; 
        color: #4B5563; 
        font-size: 1.15rem; 
        margin-bottom: 2rem; 
        font-weight: 500; 
    }
    
    /* 侧边栏优化 */
    [data-testid="stSidebar"] { width: 380px !important; min-width: 380px !important; }
    [data-testid="stSidebar"] > div { width: 380px !important; padding-right: 1rem; }
    
    /* 卡片容器 */
    .card-container { 
        background: white; 
        border-radius: 14px; 
        padding: 1.5rem; 
        margin: 1.2rem 0; 
        box-shadow: 0 2px 12px rgba(0,0,0,0.05); 
        border-top: 4px solid #6366F1; 
    }
    .card-header { 
        display: flex; 
        align-items: center; 
        gap: 0.6rem; 
        font-weight: 700; 
        color: #4338CA; 
        margin-bottom: 1rem; 
        font-size: 1.15rem; 
    }
    
    /* 标签 */
    .label-front { background: #6366F1; color: white; padding: 0.3rem 0.9rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; margin-bottom: 0.6rem; }
    .label-back { background: #10B981; color: white; padding: 0.3rem 0.9rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; margin-bottom: 0.6rem; }
    
    /* 成功横幅 */
    .success-banner { 
        background: linear-gradient(135deg, #10B981 0%, #059669 100%); 
        color: white; 
        padding: 1rem; 
        border-radius: 12px; 
        text-align: center; 
        font-weight: 600; 
        margin-bottom: 1.5rem; 
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); 
    }
    
    /* 按钮美化 */
    .stButton>button { 
        background: linear-gradient(135deg, #6366F1 0%, #4338CA 100%); 
        color: white; 
        border: none; 
        border-radius: 10px; 
        padding: 0.7rem 2rem; 
        font-weight: 600; 
        font-size: 1.05rem; 
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4); 
    }
    .stButton>button:hover { transform: translateY(-1px); }
    
    /* 隐藏默认元素 */
    #MainMenu, footer { visibility: hidden; }
    
    /* 📱 移动端适配 (屏幕宽度小于 600px) */
    @media (max-width: 600px) {
        .main-container { padding: 1rem; margin: 0.5rem; }
        .main-title { font-size: 2.2rem; }
        .subtitle { font-size: 1rem; }
        [data-testid="stSidebar"] { width: 100% !important; }
        .card-container { padding: 1rem; }
        .card-header { font-size: 1rem; }
    }
</style>
""", unsafe_allow_html=True)

# ============ 🎯 主界面逻辑 ============
def main():
    st.set_page_config(page_title="🗂️ AI Anki 智能制卡器", page_icon="🗂️", layout="wide")
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">🗂️ AI Anki 智能制卡器</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">上传资料 → 选择模式 → 生成高强度训练卷 → 一键导出 Anki</p>', unsafe_allow_html=True)
    
    # 📖 新手引导页 (可折叠)
    with st.expander("📖 新手指南 / 使用教程", expanded=False):
        st.markdown("""
        ### 🚀 快速开始
        1. **输入内容**：在左侧上传 `.txt/.pdf/.docx` 文件，或直接粘贴复习资料。
        2. **选择类型**：
           - 🕳️ **仅填空卡**：适合背诵关键词、定义（推荐）。
           - 🔄 **仅翻转卡**：适合问答、概念理解。
           - 🎲 **混合模式**：两者结合。
        3. **生成与预览**：点击“生成训练卷”，AI 会自动出题并在右侧预览。
        4. **一键复制**：每张卡片右上角有“复制”图标，点击即可复制内容。
        5. **导出 Anki**：确认无误后，点击底部“下载 .apkg 文件”，导入 Anki 桌面版即可开始复习！
        
        ### 💡 小贴士
        - 每次处理 **300~800 字** 效果最佳。
        - 导出的 `.apkg` 文件可直接拖入 Anki 电脑端或手机端。
        """)

    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.markdown("### 📥 第一步：输入内容")
        
        card_mode = st.selectbox(
            "📇 选择卡片类型", 
            ["cloze", "mixed", "basic"], 
            format_func=lambda x: {"mixed": "🎲 混合模式", "cloze": "🕳️ 仅填空卡 (推荐)", "basic": "🔄 仅翻转卡"}[x]
        )
        
        st.markdown("---")
        uploaded_file = st.file_uploader("上传文件 (.txt/.pdf/.docx)", type=["txt", "pdf", "docx"])
        
        st.markdown("---")
        text_input = st.text_area("或粘贴文字", height=220, placeholder="粘贴你的复习资料...")
        
        st.markdown("---")
        generate_btn = st.button("🚀 生成训练卷", type="primary", use_container_width=True)
        
        st.markdown("---")
        st.info("💡 **建议**\n• 每次 300~800 字效果最佳\n• 导出后可直接导入 Anki 桌面版")
        st.markdown('</div>', unsafe_allow_html=True)

    # 使用 Session State 保存生成的卡片
    if 'cards' not in st.session_state:
        st.session_state.cards = []

    if generate_btn:
        raw_text = ""
        if uploaded_file:
            file_type = uploaded_file.name.split(".")[-1].lower()
            with st.status(f"📄 正在解析 {uploaded_file.name}...", expanded=True) as status:
                try:
                    if file_type == "txt":
                        raw_text = uploaded_file.getvalue().decode("utf-8")
                    elif file_type == "pdf":
                        with open("temp.pdf", "wb") as f: f.write(uploaded_file.read())
                        reader = PdfReader("temp.pdf")
                        raw_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
                        os.remove("temp.pdf")
                    elif file_type == "docx":
                        with open("temp.docx", "wb") as f: f.write(uploaded_file.read())
                        doc = Document("temp.docx")
                        raw_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
                        os.remove("temp.docx")
                    status.update(label=f"✅ 提取 {len(raw_text)} 字符", state="complete")
                except Exception as e:
                    st.error(f"❌ 解析失败：{e}")
                    st.stop()
        elif text_input.strip():
            raw_text = text_input.strip()
        else:
            st.warning("⚠️ 请输入内容")
            st.stop()

        if raw_text:
            # ⏳ 模拟进度条 + AI 生成
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 模拟解析进度
            for i in range(100):
                time.sleep(0.02)
                progress_bar.progress(i + 1)
                if i < 30:
                    status_text.text("🤖 AI 正在分析知识点...")
                elif i < 70:
                    status_text.text("✍️ AI 正在生成填空题...")
                else:
                    status_text.text("✨ 正在优化排版...")
            
            st.session_state.cards = generate_cards(raw_text, mode=card_mode)
            progress_bar.empty()
            status_text.empty()
            
            if st.session_state.cards:
                st.success("🎉 生成成功！")
                st.balloons() # 🎈 撒花庆祝
                st.rerun()
            else:
                st.error("⚠️ 未生成有效卡片，请检查 API Key 或文本内容。")

    # 显示结果与下载
    if st.session_state.cards:
        st.markdown(f'<div class="success-banner">✨ 成功生成 {len(st.session_state.cards)} 组训练卡片</div>', unsafe_allow_html=True)
        
        for i, card in enumerate(st.session_state.cards, 1):
            t = card.get('type', 'cloze')
            emoji = "🕳️" if t == "cloze" else "🔄"
            name = "填空卡" if t == "cloze" else "翻转卡"
            
            st.markdown(f'<div class="card-container"><div class="card-header">{emoji} 卡片 {i} · {name}</div></div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<span class="label-front">🔹 正面</span>', unsafe_allow_html=True)
                # 📋 使用 st.code 实现一键复制 (右上角有复制图标)
                st.code(card.get("front", ""), language="text")
            
            with col2:
                st.markdown('<span class="label-back">🔹 背面</span>', unsafe_allow_html=True)
                st.code(card.get("back", ""), language="text")

        # 📥 下载按钮
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📦 导出到 Anki")
        try:
            apkg_path = export_to_apkg(st.session_state.cards)
            with open(apkg_path, "rb") as f:
                st.download_button(
                    label="📥 下载 .apkg 文件 (点击导入 Anki)",
                    data=f,
                    file_name="AI_Anki_Training.apkg",
                    mime="application/octet-stream",
                    use_container_width=True,
                    key="download_btn"
                )
        except Exception as e:
            st.error(f"导出失败：{e}")

    st.markdown("</div>", unsafe_allow_html=True)
    st.caption("🛠️ powered by AI · 让学习更高效")

if __name__ == "__main__":
    main()