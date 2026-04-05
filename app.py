# -*- coding: utf-8 -*-
import streamlit as st
from pypdf import PdfReader
from docx import Document
import os
import tempfile
import genanki
import json
from datetime import datetime
from main import generate_cards

# ============ 📦 核心导出函数 ============
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
        front = card.get('front', '').replace('### ', '<h3 class="section-title">').replace('**', '')
        back = card.get('back', '').replace('**', '').replace('\n', '<br>')
        model = cloze_model if t == 'cloze' else basic_model
        deck.add_note(genanki.Note(model=model, fields=[front, back]))
        
    tmp = tempfile.gettempdir()
    path = os.path.join(tmp, f"{deck_name}.apkg")
    genanki.Package(deck).write_to_file(path)
    return path

# ============ 🎨 全局 CSS ============
st.markdown("""
<style>
    .stApp { background: #F8FAFC; }
    .main-container { background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 4px 20px rgba(0,0,0,0.04); margin: 1rem auto; max-width: 1200px; }
    .page-title { font-size: 2.6rem; font-weight: 800; color: #1E293B; margin: 0 0 0.5rem; }
    .page-subtitle { color: #64748B; font-size: 1.05rem; margin-bottom: 2rem; }
    [data-testid="stSidebar"] { width: 260px !important; background: #F1F5F9 !important; padding-top: 1rem; }
    .nav-btn { background: white; border: 1px solid #E2E8F0; border-radius: 10px; padding: 0.8rem; margin: 0.4rem 0; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 0.6rem; font-weight: 600; color: #475569; }
    .nav-btn:hover, .nav-btn.active { background: #6366F1; color: white; border-color: #6366F1; transform: translateX(4px); }
    .card-box { background: #FAFBFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1.2rem; margin: 1rem 0; }
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem; font-weight: 700; color: #334155; }
    .tag { padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
    .tag-cloze { background: #DBEAFE; color: #1D4ED8; }
    .tag-basic { background: #D1FAE5; color: #047857; }
    .history-row { display: flex; justify-content: space-between; align-items: center; padding: 1rem; border-bottom: 1px solid #F1F5F9; transition: background 0.2s; }
    .history-row:hover { background: #F8FAFC; }
    #MainMenu, footer { visibility: hidden; }
    .stButton>button { background: linear-gradient(135deg, #6366F1, #4338CA); color: white; border-radius: 10px; padding: 0.6rem 1.5rem; font-weight: 600; }
    .stButton>button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(99,102,241,0.3); }
    .stCodeBlock { border-radius: 10px; margin-top: 0.5rem; }
    .save-btn { background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 0.4rem 0.8rem; font-size: 0.85rem; }
    .save-btn:hover { background: #E2E8F0; }
    @media (max-width: 600px) { .main-container { padding: 1rem; } .page-title { font-size: 2rem; } }
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

    # 侧边栏导航
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;color:#1E293B;margin-bottom:1.5rem;'>🗂️ AI Anki</h2>", unsafe_allow_html=True)
        pages = ["🛠️ 制作", "📜 历史记录", "💾 已保存的卡"]
        for p in pages:
            page_key = p.split()[-1]
            btn_class = "nav-btn active" if st.session_state.page == page_key else "nav-btn"
            if st.button(p, key=f"nav_{page_key}", use_container_width=True):
                st.session_state.page = page_key
                st.rerun()
        
        st.markdown("---")
        st.caption("💡 提示：刷新会清空数据，建议定期备份。")
        
        # 数据备份/恢复
        if st.button("📥 导出备份(JSON)", use_container_width=True):
            backup = {"history": st.session_state.history, "saved": st.session_state.saved}
            st.download_button("⬇️ 下载备份", json.dumps(backup, ensure_ascii=False), "anki_backup.json", "application/json", use_container_width=True)
            
        uploaded_backup = st.file_uploader("📤 导入备份(JSON)", type=["json"], label_visibility="collapsed")
        if uploaded_backup:
            try:
                data = json.load(uploaded_backup)
                st.session_state.history = data.get("history", [])
                st.session_state.saved = data.get("saved", [])
                st.success("✅ 恢复成功！")
                st.rerun()
            except: st.error("❌ 备份文件损坏")

    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # ================= 🛠️ 制作页面 =================
    if st.session_state.page == '制作':
        st.markdown('<h1 class="page-title">🛠️ 卡片制作</h1>', unsafe_allow_html=True)
        st.markdown('<p class="page-subtitle">上传资料或粘贴文本，AI 自动生成高强度训练卷</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            mode = st.selectbox("卡片类型", ["cloze", "basic", "mixed"], format_func=lambda x: {"mixed":"🎲 混合","cloze":"🕳️ 填空","basic":"🔄 翻转"}[x])
            file = st.file_uploader("上传文件", type=["txt","pdf","docx"])
            text = st.text_area("或粘贴文本", height=200)
            
            if st.button("🚀 开始生成", type="primary", use_container_width=True):
                raw = ""
                if file:
                    ft = file.name.split(".")[-1]
                    if ft=="txt": raw=file.getvalue().decode("utf-8")
                    elif ft=="pdf":
                        with open("t.pdf","wb") as f: f.write(file.read())
                        raw="\n".join([p.extract_text() for p in PdfReader("t.pdf").pages])
                        os.remove("t.pdf")
                    elif ft=="docx":
                        with open("t.docx","wb") as f: f.write(file.read())
                        raw="\n".join([p.text for p in Document("t.docx").paragraphs])
                        os.remove("t.docx")
                elif text.strip(): raw = text.strip()
                else: st.warning("请输入内容"); st.stop()
                
                with st.spinner("🤖 AI 生成中..."):
                    st.session_state.current_cards = generate_cards(raw, mode)
                if st.session_state.current_cards:
                    rec = {"time": datetime.now().strftime("%m-%d %H:%M"), "count": len(st.session_state.current_cards), "preview": raw[:50]+"...", "cards": st.session_state.current_cards}
                    st.session_state.history.insert(0, rec)
                    st.success(f"✨ 生成 {len(st.session_state.current_cards)} 张卡片！"); st.balloons()
                    st.rerun()

        with col2:
            if st.session_state.current_cards:
                for i, c in enumerate(st.session_state.current_cards):
                    t = c.get('type','cloze')
                    with st.container():
                        st.markdown(f"""
                        <div class="card-box">
                            <div class="card-header">
                                <span>📇 卡片 {i+1} <span class="tag {'tag-cloze' if t=='cloze' else 'tag-basic'}">{t.upper()}</span></span>
                                <button class="save-btn" onclick="navigator.clipboard.writeText(`{c['front'].replace('`','\\`')}`).then(()=>this.innerText='已保存!')">💾 保存单卡</button>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col_f, col_b = st.columns(2)
                        with col_f:
                            st.markdown("**🔹 正面** (点击代码块右上角 📋 复制)")
                            st.code(c['front'], language=None)
                        with col_b:
                            st.markdown("**🔹 背面**")
                            st.code(c['back'], language=None)
                            
                        # 原生保存按钮
                        if st.button("⭐ 添加到收藏库", key=f"save_{i}"):
                            st.session_state.saved.append(c)
                            st.success("✅ 已收藏！")
                
                # 导出当前批次
                if st.button("📦 导出当前批次为 .apkg", use_container_width=True, type="secondary"):
                    path = export_to_apkg(st.session_state.current_cards, f"Batch_{datetime.now().strftime('%m%d')}")
                    with open(path,"rb") as f: st.download_button("⬇️ 下载 .apkg", f, "current_batch.apkg", "application/octet-stream", use_container_width=True)

    # ================= 📜 历史记录页面 =================
    elif st.session_state.page == '历史记录':
        st.markdown('<h1 class="page-title">📜 历史记录</h1>', unsafe_allow_html=True)
        st.markdown('<p class="page-subtitle">查看过往生成记录，可重新加载或导出</p>', unsafe_allow_html=True)
        
        if not st.session_state.history:
            st.info("📭 暂无记录，去“制作”页面生成一些卡片吧！")
        else:
            if st.button("🗑️ 清空历史", key="clear_hist"): st.session_state.history=[]; st.rerun()
            for idx, rec in enumerate(st.session_state.history):
                st.markdown(f"""
                <div class="history-row">
                    <div>
                        <div style="font-weight:600;color:#1E293B;">{rec['time']} · {rec['count']} 张卡片</div>
                        <div style="font-size:0.85rem;color:#64748B;">{rec['preview']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col_a, col_b, col_c = st.columns([1, 1, 1])
                with col_a:
                    if st.button("📂 加载回制作页", key=f"load_{idx}"):
                        st.session_state.current_cards = rec['cards']
                        st.session_state.page = '制作'
                        st.rerun()
                with col_b:
                    if st.button("🗑️ 删除记录", key=f"del_{idx}"):
                        st.session_state.history.pop(idx)
                        st.rerun()
                with col_c:
                    if st.button("📥 导出此记录", key=f"exp_{idx}"):
                        path = export_to_apkg(rec['cards'], f"History_{idx}")
                        with open(path,"rb") as f: st.download_button("⬇️", f, f"history_{idx}.apkg", "application/octet-stream")

            # 导出全部历史
            all_cards = [c for r in st.session_state.history for c in r['cards']]
            if all_cards and st.button("📦 导出全部历史记录", use_container_width=True, type="secondary"):
                path = export_to_apkg(all_cards, "All_History")
                with open(path,"rb") as f: st.download_button("⬇️ 下载全部 .apkg", f, "all_history.apkg", "application/octet-stream", use_container_width=True)

    # ================= 💾 已保存的卡页面 =================
    elif st.session_state.page == '已保存的卡':
        st.markdown('<h1 class="page-title">💾 已保存的卡</h1>', unsafe_allow_html=True)
        st.markdown('<p class="page-subtitle">收藏的优质卡片库，支持筛选与批量导出</p>', unsafe_allow_html=True)
        
        if not st.session_state.saved:
            st.info("💎 暂无收藏卡片，在“制作”页面点击“⭐ 添加到收藏库”即可加入。")
        else:
            filter_type = st.radio("筛选类型", ["全部", "cloze", "basic"], horizontal=True)
            display_cards = [c for c in st.session_state.saved if filter_type=="全部" or c.get('type')==filter_type]
            
            if st.button("🗑️ 清空收藏", key="clear_saved"): st.session_state.saved=[]; st.rerun()
            
            cols = st.columns(2)
            for i, c in enumerate(display_cards):
                t = c.get('type','cloze')
                col = cols[i%2]
                with col:
                    st.markdown(f"""
                    <div class="card-box">
                        <div style="display:flex;justify-content:space-between;margin-bottom:0.5rem;">
                            <span class="tag {'tag-cloze' if t=='cloze' else 'tag-basic'}">{t.upper()}</span>
                            <span style="font-size:0.8rem;color:#94A3B8;">#{st.session_state.saved.index(c)+1}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("**正面预览**")
                    st.text(c['front'][:150] + "..." if len(c['front'])>150 else c['front'])
                    
                    if st.button("🗑️ 删除此卡", key=f"del_saved_{i}"):
                        st.session_state.saved.remove(c)
                        st.rerun()
            
            if display_cards and st.button("📦 导出当前筛选列表", use_container_width=True, type="secondary"):
                path = export_to_apkg(display_cards, "Saved_Cards")
                with open(path,"rb") as f: st.download_button("⬇️ 下载 .apkg", f, "saved_cards.apkg", "application/octet-stream", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()