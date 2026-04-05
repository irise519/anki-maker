# -*- coding: utf-8 -*-
import streamlit as st
from pypdf import PdfReader
from docx import Document
import os
import tempfile
import genanki
import json
import re
from datetime import datetime
from main import generate_cards

# ============ 🎨 核心工具函数 ============
def format_cloze_text(text, show_answer=False):
    """
    将 Anki 语法 {{c1::答案}} 转换为 Markdown 高亮样式
    """
    if not text:
        return ""
    
    # 先清理可能的 HTML 标签
    text = re.sub(r'<[^>]+>', '', text)
    
    # 正则匹配 {{c1::答案}} 或 {{c1::答案::提示}}
    pattern = r'\{\{c\d+::(.*?)(?:::.+?)?\}\}'
    
    if show_answer:
        # 背面：显示答案，用 **加粗** 和 ==高亮==
        def replacer_show(match):
            content = match.group(1)
            return f'**{content}**'
        result = re.sub(pattern, replacer_show, text)
    else:
        # 正面：显示挖空，用 [___] 表示
        def replacer_hide(match):
            return '[___]'
        result = re.sub(pattern, replacer_hide, text)
    
    return result

def export_to_apkg(cards, deck_name="AI_导出牌组"):
    cloze_model = genanki.Model(
        1607392319, 'AI_Cloze_Model',
        fields=[{'name': 'Text', 'type': 'CLOZE'}, {'name': 'Extra'}],
        templates=[{'name': 'Cloze', 'qfmt': '{{cloze:Text}}', 'afmt': '{{cloze:Text}}<hr id="answer"><div class="answer-box">{{Extra}}</div>'}],
        css='.card { font-family: "PingFang SC", sans-serif; font-size: 18px; line-height: 1.6; } h3.section-title { background:#EEF2FF; color:#4338CA; padding:6px 10px; border-radius:6px; font-size:0.85em; border-left:3px solid #6366F1; } .cloze { color:#2563EB; background:#DBEAFE; padding:1px 4px; border-radius:3px; } .answer-box { background:#F0FDF4; padding:12px; border-radius:8px; border-left:3px solid #10B981; margin-top:15px; }'
    )
    basic_model = genanki.Model(
        1584563748, 'AI_Basic_Model',
        fields=[{'name': 'Question'}, {'name': 'Answer'}],
        templates=[{'name': 'Card 1', 'qfmt': '{{Question}}', 'afmt': '{{FrontSide}}<hr id="answer"><div class="answer-box">{{Answer}}</div>'}],
        css='.card { font-family: "PingFang SC", sans-serif; font-size: 18px; } .answer-box { background:#F0FDF4; padding:12px; border-radius:8px; border-left:3px solid #10B981; margin-top:15px; }'
    )
    
    deck = genanki.Deck(1584563749, deck_name)
    for card in cards:
        t = card.get('type', 'cloze')
        front = card.get('front', '').replace('### ', '#### ').replace('**', '')
        back = card.get('back', '').replace('**', '').replace('\n', '\n\n')
        model = cloze_model if t == 'cloze' else basic_model
        deck.add_note(genanki.Note(model=model, fields=[front, back]))
        
    tmp = tempfile.gettempdir()
    path = os.path.join(tmp, f"{deck_name}.apkg")
    genanki.Package(deck).write_to_file(path)
    return path

# ============ 🎨 全局 CSS ============
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    body { font-family: 'Inter', "PingFang SC", sans-serif; }
    .stApp { background: #F3F4F6; }
    
    .main-container { background: white; border-radius: 20px; padding: 2.5rem; box-shadow: 0 10px 40px rgba(0,0,0,0.05); margin: 1rem auto; max-width: 1200px; }
    
    .page-title { font-size: 2.8rem; font-weight: 800; color: #111827; margin: 0 0 0.5rem; }
    .page-subtitle { color: #6B7280; font-size: 1.1rem; margin-bottom: 2.5rem; }
    
    [data-testid="stSidebar"] { width: 280px !important; background: #FFFFFF !important; border-right: 1px solid #F3F4F6; }
    
    .nav-btn { background: white; border: 1px solid #E5E7EB; border-radius: 12px; padding: 0.9rem 1rem; margin: 0.5rem 0; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 0.8rem; font-weight: 600; color: #4B5563; }
    .nav-btn:hover { background: #F9FAFB; transform: translateX(4px); }
    .nav-btn.active { background: #4F46E5; color: white; border-color: #4F46E5; box-shadow: 0 4px 12px rgba(79, 70, 229, 0.2); }
    
    .flashcard { 
        background: #FFFFFF; 
        border: 2px solid #E5E7EB; 
        border-radius: 16px; 
        padding: 1.5rem; 
        margin: 1.5rem 0; 
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
        transition: all 0.3s ease;
        border-left: 5px solid #4F46E5;
    }
    .flashcard:hover { 
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08); 
        transform: translateY(-2px);
        border-color: #C7D2FE;
    }
    
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.2rem; padding-bottom: 0.8rem; border-bottom: 2px solid #F3F4F6; }
    .card-title { font-size: 1.1rem; font-weight: 700; color: #1F2937; }
    
    .badge { padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.75rem; font-weight: 700; }
    .badge-cloze { background: #EEF2FF; color: #4338CA; }
    .badge-basic { background: #ECFDF5; color: #047857; }
    
    .content-box { 
        background: #F9FAFB; 
        padding: 1.2rem; 
        border-radius: 10px; 
        margin: 0.8rem 0;
        border: 1px solid #F3F4F6;
    }
    
    .content-label { 
        font-size: 0.85rem; 
        font-weight: 600; 
        color: #6B7280; 
        text-transform: uppercase; 
        letter-spacing: 0.05em; 
        margin-bottom: 0.5rem; 
    }
    
    .front-text { font-size: 1.05rem; line-height: 1.8; color: #1F2937; }
    .back-text { font-size: 1.05rem; line-height: 1.8; color: #047857; background: #ECFDF5; padding: 1rem; border-radius: 8px; }
    
    .cloze-highlight { 
        background: #FDE68A; 
        color: #92400E; 
        padding: 0 6px; 
        border-radius: 4px; 
        font-weight: 700; 
        border-bottom: 2px solid #F59E0B;
    }
    
    .answer-highlight { 
        background: #6EE7B7; 
        color: #065F46; 
        padding: 0 6px; 
        border-radius: 4px; 
        font-weight: 700; 
    }
    
    .history-item { 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        padding: 1.2rem; 
        border-radius: 12px; 
        background: #F9FAFB; 
        margin-bottom: 0.8rem; 
        border: 1px solid #F3F4F6; 
        transition: all 0.2s; 
    }
    .history-item:hover { background: #FFFFFF; border-color: #E5E7EB; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    
    #MainMenu, footer { visibility: hidden; }
    
    .stButton>button { 
        background: #4F46E5; 
        color: white; 
        border-radius: 10px; 
        padding: 0.6rem 1.5rem; 
        font-weight: 600; 
        border: none; 
    }
    .stButton>button:hover { 
        background: #4338CA; 
        transform: translateY(-1px); 
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3); 
    }
    
    @media (max-width: 768px) { 
        .main-container { padding: 1.5rem; } 
        .page-title { font-size: 2rem; } 
    }
</style>
""", unsafe_allow_html=True)

# ============ 🎯 主程序 ============
def main():
    st.set_page_config(page_title="🗂️ AI Anki 智能制卡器", page_icon="🗂️", layout="wide")
    
    # 初始化状态
    if 'page' not in st.session_state: st.session_state.page = '制作'
    if 'history' not in st.session_state: st.session_state.history = []
    if 'saved' not in st.session_state: st.session_state.saved = []
    if 'current_cards' not in st.session_state: st.session_state.current_cards = []

    # 侧边栏
    with st.sidebar:
        st.markdown("<div style='text-align:center;padding:1rem 0;'><h2 style='margin:0;color:#4F46E5;'>🗂️ AI Anki</h2><span style='font-size:0.8rem;color:#9CA3AF;'>Pro Card Maker</span></div>", unsafe_allow_html=True)
        pages = ["🛠️ 制作中心", "📜 历史记录", "💾 我的收藏"]
        for p in pages:
            page_key = p.split()[1] if len(p.split())>1 else p
            btn_class = "nav-btn active" if st.session_state.page == page_key else "nav-btn"
            if st.button(p, key=f"nav_{page_key}", use_container_width=True):
                st.session_state.page = page_key
                st.rerun()
        
        st.markdown("---")
        st.caption("💡 提示：刷新会清空数据，建议定期备份。")
        
        if st.button("📥 导出备份(JSON)", use_container_width=True):
            backup = {"history": st.session_state.history, "saved": st.session_state.saved}
            st.download_button("⬇️ 下载备份", json.dumps(backup, ensure_ascii=False), "anki_backup.json", "application/json", use_container_width=True)
            
        uploaded_backup = st.file_uploader("📤 导入备份", type=["json"], label_visibility="collapsed")
        if uploaded_backup:
            try:
                data = json.load(uploaded_backup)
                st.session_state.history = data.get("history", [])
                st.session_state.saved = data.get("saved", [])
                st.success("✅ 恢复成功！"); st.rerun()
            except: st.error("❌ 备份文件损坏")

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # ================= 🛠️ 制作页面 =================
    if st.session_state.page == '制作':
        st.markdown('<h1 class="page-title">🛠️ 卡片制作中心</h1>', unsafe_allow_html=True)
        st.markdown('<p class="page-subtitle">上传资料或粘贴文本，AI 自动生成高强度训练卷</p>', unsafe_allow_html=True)
        
        col_input, col_preview = st.columns([1, 2])
        
        with col_input:
            st.markdown("### 📥 输入设置")
            mode = st.selectbox("卡片类型", ["cloze", "basic", "mixed"], format_func=lambda x: {"mixed":"🎲 混合模式","cloze":"🕳️ 填空卡 (推荐)","basic":"🔄 翻转卡"}[x])
            file = st.file_uploader("上传文件", type=["txt","pdf","docx"])
            text = st.text_area("或粘贴文本", height=250, placeholder="在此粘贴你的复习资料...")
            
            if st.button("🚀 开始生成", type="primary", use_container_width=True):
                raw = ""
                if file:
                    ft = file.name.split(".")[-1]
                    try:
                        if ft=="txt": raw=file.getvalue().decode("utf-8")
                        elif ft=="pdf":
                            with open("t.pdf","wb") as f: f.write(file.read())
                            raw="\n".join([p.extract_text() for p in PdfReader("t.pdf").pages])
                            os.remove("t.pdf")
                        elif ft=="docx":
                            with open("t.docx","wb") as f: f.write(file.read())
                            raw="\n".join([p.text for p in Document("t.docx").paragraphs])
                            os.remove("t.docx")
                    except Exception as e: st.error(f"文件解析失败: {e}"); st.stop()
                elif text.strip(): raw = text.strip()
                else: st.warning("请输入内容"); st.stop()
                
                with st.spinner("🤖 AI 正在思考并生成卡片..."):
                    st.session_state.current_cards = generate_cards(raw, mode)
                
                if st.session_state.current_cards:
                    rec = {"time": datetime.now().strftime("%m-%d %H:%M"), "count": len(st.session_state.current_cards), "preview": raw[:50]+"...", "cards": st.session_state.current_cards}
                    st.session_state.history.insert(0, rec)
                    st.success(f"✨ 成功生成 {len(st.session_state.current_cards)} 张卡片！"); st.balloons()
                    st.rerun()
                else:
                    st.error("❌ 生成失败，请检查 API 或文本内容。")

        with col_preview:
            if st.session_state.current_cards:
                st.markdown(f"### 📋 预览结果 ({len(st.session_state.current_cards)} 张)")
                
                for i, c in enumerate(st.session_state.current_cards):
                    t = c.get('type','cloze')
                    badge_class = "badge-cloze" if t=='cloze' else "badge-basic"
                    badge_name = "FILL_BLANK" if t=='cloze' else "Q&A"
                    
                    # 处理文本 - 正面（挖空）
                    front_raw = c.get('front', '')
                    front_clean = front_raw.replace('### ', '').replace('**', '')
                    front_display = format_cloze_text(front_clean, show_answer=False)
                    
                    # 处理文本 - 背面（答案）
                    back_raw = c.get('back', '')
                    back_clean = back_raw.replace('**', '').replace('\n', ' ')
                    back_display = format_cloze_text(back_clean, show_answer=True)
                    
                    # 使用 Streamlit 原生组件显示
                    with st.container():
                        st.markdown(f"""
                        <div class="flashcard">
                            <div class="card-header">
                                <div class="card-title">📇 卡片 #{i+1}</div>
                                <span class="badge {badge_class}">{badge_name}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 正面
                        st.markdown('<div class="content-label">🔹 正面（问题）</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="content-box front-text">{front_display}</div>', unsafe_allow_html=True)
                        
                        # 背面
                        st.markdown('<div class="content-label">🔸 背面（答案）</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="content-box back-text">{back_display}</div>', unsafe_allow_html=True)
                        
                        # 操作按钮
                        col1, col2, col3 = st.columns([1, 1, 2])
                        with col1:
                            if st.button("📋 复制正面", key=f"copy_f_{i}"):
                                st.code(front_clean, language=None)
                        with col2:
                            if st.button("📋 复制背面", key=f"copy_b_{i}"):
                                st.code(back_clean, language=None)
                        with col3:
                            if st.button("⭐ 收藏此卡", key=f"save_{i}"):
                                st.session_state.saved.append(c)
                                st.toast("✅ 已添加到收藏库！", icon="💎")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                
                # 底部导出
                st.markdown("---")
                if st.button("📦 导出当前批次为 .apkg", type="secondary", use_container_width=True):
                    path = export_to_apkg(st.session_state.current_cards, f"Batch_{datetime.now().strftime('%m%d')}")
                    with open(path,"rb") as f: st.download_button("⬇️ 下载 .apkg 文件", f, "current_batch.apkg", "application/octet-stream", use_container_width=True)

    # ================= 📜 历史记录页面 =================
    elif st.session_state.page == '历史':
        st.markdown('<h1 class="page-title">📜 历史记录</h1>', unsafe_allow_html=True)
        st.markdown('<p class="page-subtitle">查看过往生成记录，支持重新加载或导出</p>', unsafe_allow_html=True)
        
        if not st.session_state.history:
            st.info("📭 暂无记录，快去制作卡片吧！")
        else:
            if st.button("🗑️ 清空所有历史", key="clear_hist"): st.session_state.history=[]; st.rerun()
            
            for idx, rec in enumerate(st.session_state.history):
                st.markdown(f"""
                <div class="history-item">
                    <div>
                        <div style="font-weight:700;color:#1F2937;font-size:1.05rem;">{rec['time']}</div>
                        <div style="font-size:0.9rem;color:#6B7280;margin-top:0.2rem;">{rec['count']} 张卡片 · {rec['preview'][:40]}...</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns([2, 1, 1])
                with c1:
                    if st.button("📂 加载回制作页", key=f"load_{idx}"):
                        st.session_state.current_cards = rec['cards']
                        st.session_state.page = '制作'
                        st.rerun()
                with c2:
                    if st.button("🗑️ 删除", key=f"del_{idx}"):
                        st.session_state.history.pop(idx)
                        st.rerun()
                with c3:
                    if st.button("📥 导出", key=f"exp_{idx}"):
                        path = export_to_apkg(rec['cards'], f"History_{idx}")
                        with open(path,"rb") as f: st.download_button("⬇️", f, f"history_{idx}.apkg", "application/octet-stream")

            all_cards = [c for r in st.session_state.history for c in r['cards']]
            if all_cards and st.button("📦 导出全部历史记录", type="secondary", use_container_width=True):
                path = export_to_apkg(all_cards, "All_History")
                with open(path,"rb") as f: st.download_button("⬇️ 下载全部 .apkg", f, "all_history.apkg", "application/octet-stream", use_container_width=True)

    # ================= 💾 收藏页面 =================
    elif st.session_state.page == '收藏':
        st.markdown('<h1 class="page-title">💾 我的收藏库</h1>', unsafe_allow_html=True)
        st.markdown('<p class="page-subtitle">精心挑选的优质卡片，支持筛选与批量导出</p>', unsafe_allow_html=True)
        
        if not st.session_state.saved:
            st.info("💎 暂无收藏，在制作页点击"⭐ 收藏此卡"即可加入。")
        else:
            filter_type = st.radio("筛选类型", ["全部", "cloze", "basic"], horizontal=True)
            display_cards = [c for c in st.session_state.saved if filter_type=="全部" or c.get('type')==filter_type]
            
            if st.button("🗑️ 清空收藏", key="clear_saved"): st.session_state.saved=[]; st.rerun()
            
            cols = st.columns(2)
            for i, c in enumerate(display_cards):
                t = c.get('type','cloze')
                badge_class = "badge-cloze" if t=='cloze' else "badge-basic"
                front_preview = format_cloze_text(c.get('front', '').replace('### ', '').replace('**', ''), show_answer=False)
                
                col = cols[i%2]
                with col:
                    st.markdown(f"""
                    <div class="flashcard" style="margin:0.5rem 0;">
                        <div class="card-header" style="margin-bottom:0.5rem;">
                            <span class="badge {badge_class}">{t.upper()}</span>
                            <span style="font-size:0.8rem;color:#9CA3AF;">#{st.session_state.saved.index(c)+1}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(f'<div style="font-size:0.9rem;line-height:1.6;color:#4B5563;">{front_preview[:150]}...</div>', unsafe_allow_html=True)
                    
                    if st.button("🗑️ 删除", key=f"del_saved_{i}"):
                        st.session_state.saved.remove(c)
                        st.rerun()
            
            if display_cards and st.button("📦 导出当前筛选列表", type="secondary", use_container_width=True):
                path = export_to_apkg(display_cards, "Saved_Cards")
                with open(path,"rb") as f: st.download_button("⬇️ 下载 .apkg", f, "saved_cards.apkg", "application/octet-stream", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()