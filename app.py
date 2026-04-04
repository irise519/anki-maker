# -*- coding: utf-8 -*-
import streamlit as st
import pdfplumber
from docx import Document
import os
import tempfile
import genanki
from main import generate_cards

# ============ 📦 核心导出函数 ============
# ============ 📦 核心导出函数 ============
def export_to_apkg(cards, deck_name="AI_专项训练卷"):
    """将卡片列表打包为 .apkg 文件，自动区分填空卡和翻转卡"""
    
    # 1. 定义填空卡模型 (Cloze Model)
    cloze_model = genanki.Model(
        1607392319,
        'AI_Cloze_Model',
        fields=[
            {'name': 'Text', 'type': 'CLOZE'},
            {'name': 'Extra'}
        ],
        templates=[
            {
                'name': 'Cloze',
                'qfmt': '{{cloze:Text}}<br><div style="font-size:0.8em;color:#666;margin-top:10px;">{{Extra}}</div>',
                'afmt': '{{cloze:Text}}<hr id="answer"><div class="answer-box">{{Extra}}</div>'
            },
        ],
        css="""
        /* 全局卡片样式 */
        .card { font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; font-size: 19px; line-height: 1.7; color: #1f2937; background-color: #ffffff; padding: 10px; }
        
        /* 章节标题样式 */
        h3.section-title { 
            background: #EEF2FF; 
            color: #4338CA; 
            padding: 8px 12px; 
            border-radius: 8px; 
            margin: 0 0 15px 0; 
            font-size: 0.9em; 
            font-weight: 700; 
            border-left: 5px solid #6366F1; 
        }

        /* ★★★ 核心：挖空样式改造 ★★★ */
        /* 将默认的 [...] 变为“填空题横线”效果 */
        .cloze { 
            color: #B45309; /* 深橙色文字（即使被隐藏也保留颜色痕迹） */
            background: #FEF3C7; /* 浅黄色背景，像试卷填空区 */
            padding: 2px 8px; 
            border-radius: 6px; 
            font-weight: bold; 
            border-bottom: 2px solid #F59E0B; /* 底部加粗横线 */
        }

        /* 答案区域美化 */
        #answer { display: none; }
        .answer-box { 
            text-align: left; 
            background: #F0FDF4; /* 浅绿色背景 */
            padding: 20px; 
            border-radius: 12px; 
            border-left: 5px solid #10B981; 
            margin-top: 25px; 
            font-size: 0.95em; 
            color: #14532D; 
            line-height: 1.8;
        }
        
        /* 段落间距 */
        p { margin-bottom: 12px; }
        br { margin-bottom: 8px; }
        """
    )
    
    # 2. 定义翻转卡模型 (Basic Model)
    basic_model = genanki.Model(
        1584563748,
        'AI_Basic_Model',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'}
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '<div style="font-size:1.1em;line-height:1.6;">{{Question}}</div>',
                'afmt': '{{FrontSide}}<hr id="answer"><div class="answer-box" style="margin-top:20px;">{{Answer}}</div>'
            },
        ],
        css="""
        .card { font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; font-size: 19px; color: #1f2937; }
        h3.section-title { background: #EEF2FF; color: #4338CA; padding: 8px 12px; border-radius: 8px; margin: 12px 0 8px; font-size: 0.85em; font-weight: 600; border-left: 4px solid #6366F1; }
        .answer-box { text-align: left; background: #F9FAFB; padding: 16px; border-radius: 10px; border-left: 4px solid #10B981; font-size: 0.95em; color: #374151; }
        """
    )
    
    # 3. 创建牌组
    deck = genanki.Deck(1584563749, deck_name)
    
    # 4. 遍历卡片，根据类型选择模型
    for card in cards:
        card_type = card.get('type', 'cloze')
        front = card.get('front', '')
        back = card.get('back', '')
        
        # 清理格式
        front_clean = front.replace('### ', '<h3 class="section-title">').replace('**', '')
        back_clean = back.replace('**', '').replace('\n', '<br>')
        
        if card_type == 'cloze':
            # 填空卡：使用 Cloze 模型
            note = genanki.Note(model=cloze_model, fields=[front_clean, back_clean])
        else:
            # 翻转卡：使用 Basic 模型
            note = genanki.Note(model=basic_model, fields=[front_clean, back_clean])
        
        deck.add_note(note)
    
    # 5. 导出文件
    tmp_dir = tempfile.gettempdir()
    apkg_path = os.path.join(tmp_dir, f"{deck_name}.apkg")
    genanki.Package(deck).write_to_file(apkg_path)
    return apkg_path


# ============ 🎨 网页 UI 样式 ============
st.markdown("""
<style>
    [data-testid="stSidebar"] { width: 380px !important; min-width: 380px !important; }
    [data-testid="stSidebar"] > div { width: 380px !important; padding-right: 1rem; }
    .main-title { font-size: 3.2rem; font-weight: 800; color: #4338CA !important; text-align: center; margin: 1.5rem 0 0.5rem; text-shadow: 2px 2px 8px rgba(67, 56, 202, 0.25); }
    .subtitle { text-align: center; color: #4B5563; font-size: 1.15rem; margin-bottom: 2rem; font-weight: 500; }
    div[data-testid="column"] { display: flex !important; flex-direction: column !important; }
    .card-side { flex: 1 !important; display: flex !important; flex-direction: column !important; }
    .content-box { flex-grow: 1 !important; min-height: 150px; display: flex !important; align-items: flex-start !important; padding: 1.2rem !important; background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 10px; font-size: 0.95rem; line-height: 1.8; white-space: pre-wrap; text-align: left; }
    .stApp { background: #F3F4F6; }
    .main-container { background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 24px rgba(0,0,0,0.06); margin: 1rem auto; max-width: 1100px; }
    .success-banner { background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: white; padding: 1rem; border-radius: 12px; text-align: center; font-weight: 600; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3); }
    .card-container { background: white; border-radius: 14px; padding: 1.5rem; margin: 1.2rem 0; box-shadow: 0 2px 12px rgba(0,0,0,0.05); border-top: 4px solid #6366F1; }
    .card-header { display: flex; align-items: center; gap: 0.6rem; font-weight: 700; color: #4338CA; margin-bottom: 1rem; font-size: 1.15rem; }
    .label-front { background: #6366F1; color: white; padding: 0.3rem 0.9rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; margin-bottom: 0.6rem; }
    .label-back { background: #10B981; color: white; padding: 0.3rem 0.9rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-block; margin-bottom: 0.6rem; }
    .stButton>button { background: linear-gradient(135deg, #6366F1 0%, #4338CA 100%); color: white; border: none; border-radius: 10px; padding: 0.7rem 2rem; font-weight: 600; font-size: 1.05rem; box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4); }
    .stButton>button:hover { transform: translateY(-1px); }
    .sidebar-content { padding: 0.5rem 0; }
    #MainMenu, footer { visibility: hidden; }
    .download-btn { background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%) !important; }
</style>
""", unsafe_allow_html=True)

# ============ 🎯 主界面逻辑 ============
def main():
    st.set_page_config(page_title="🗂️ AI Anki 智能制卡器", page_icon="🗂️", layout="wide")
    
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">🗂️ AI Anki 智能制卡器</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">上传资料 → 选择模式 → 生成高强度训练卷 → 一键导出 Anki</p>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.markdown("### 📥 第一步：输入内容")
        card_mode = st.selectbox("📇 选择卡片类型", ["cloze", "mixed", "basic"], format_func=lambda x: {"mixed": "🎲 混合模式", "cloze": "🕳️ 仅填空卡 (推荐)", "basic": "🔄 仅翻转卡"}[x])
        st.markdown("---")
        uploaded_file = st.file_uploader("上传文件 (.txt/.pdf/.docx)", type=["txt", "pdf", "docx"])
        st.markdown("---")
        text_input = st.text_area("或粘贴文字", height=220, placeholder="粘贴你的复习资料...")
        st.markdown("---")
        generate_btn = st.button("🚀 生成训练卷", type="primary", use_container_width=True)
        st.markdown("---")
        st.info("💡 **建议**\n• 每次 300~800 字效果最佳\n• 导出后可直接导入 Anki 桌面版")
        st.markdown('</div>', unsafe_allow_html=True)

    # 使用 Session State 保存生成的卡片，防止刷新丢失
    if 'cards' not in st.session_state:
        st.session_state.cards = []

    if generate_btn:
        raw_text = ""
        if uploaded_file:
            file_type = uploaded_file.name.split(".")[-1].lower()
            with st.status(f"📄 解析中...", expanded=True) as status:
                try:
                    if file_type == "txt": raw_text = uploaded_file.getvalue().decode("utf-8")
from pypdf import PdfReader
# ...
elif file_type == "pdf":
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())
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
                    st.error(f"❌ 解析失败：{e}"); st.stop()
        elif text_input.strip(): raw_text = text_input.strip()
        else: st.warning("⚠️ 请输入内容"); st.stop()

        if raw_text:
            with st.spinner("🤖 AI 正在生成高强度训练卷..."):
                st.session_state.cards = generate_cards(raw_text, mode=card_mode)
            st.rerun()
            # ... 原有代码 ...
            with st.spinner("🤖 AI 正在生成高强度训练卷..."):
                cards = generate_cards(raw_text, mode=card_mode)
            
            # 🔍 调试：打印 AI 返回的原始数据
            st.write("📊 调试信息 - 生成的卡片数量:", len(cards))
            if cards:
                st.write("📄 第一张卡片预览:", cards[0])
            else:
                st.error("⚠️ AI 未返回任何卡片，请检查：\n1. API Key 是否有效\n2. 文本内容是否足够长（至少 200 字）\n3. 终端是否有报错")
                st.stop()
      
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
                st.markdown('<div class="card-side"><span class="label-front">🔹 正面</span>', unsafe_allow_html=True)
                st.markdown(f'<div class="content-box">{card.get("front", "")}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="card-side"><span class="label-back">🔹 背面</span>', unsafe_allow_html=True)
                st.markdown(f'<div class="content-box">{card.get("back", "")}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

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