# -*- coding: utf-8 -*-
import streamlit as st
from pypdf import PdfReader
from docx import Document
import os
import tempfile
import genanki
import time
import json
from datetime import datetime
from main import generate_cards

# ============ 📦 核心导出函数 ============
def export_to_apkg(cards, deck_name="AI_导出牌组"):
    """通用导出函数，支持任意卡片列表"""
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
    .page-title { font-size: 2.8rem; font-weight: 800; color: #1E293B; margin: 0 0 0.5rem; }
    .page-subtitle { color: #64748B; font-size: 1.1rem; margin-bottom: 2rem; }
    [data-testid="stSidebar"] { width: 260px !important; background: #F1F5F9 !important; }
    .nav-btn { background: white; border: 1px solid #E2E8F0; border-radius: 10px; padding: 0.8rem; margin: 0.4rem 0; cursor: pointer; transition: all 0.2s; display: flex; align-items: center; gap: 0.6rem; font-weight: 600; color: #475569; }
    .nav-btn:hover, .nav-btn.active { background: #6366F1; color: white; border-color: #6366F1; transform: translateX(4px); }
    .card-box { background: #FAFBFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1rem; margin: 0.8rem 0; }
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem; font-weight: 700; color: #334155; }
    .tag { padding: 0.2rem 0.6rem; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
    .tag-cloze { background: #DBEAFE; color: #1D4ED8; }
    .tag-basic { background: #D1FAE5; color: #047857; }
    .btn-action { background: #F8FAFC; border: 1px solid #CBD5E1; border-radius: 8px; padding: 0.4rem 0.8rem; font-size: 0.85rem; cursor: pointer; }
    .btn-action:hover { background: #E2E8F0; }
    .history-row { display: flex; justify-content: space-between; align-items: center; padding: 1rem; border-bottom: 1px solid #F1F5F9; }
    .history-row:hover { background: #F8FAFC; }
    #MainMenu, footer { visibility: hidden; }
    .stButton>button { background: linear-gradient(135deg, #6366F1, #4338CA); color: white; border-radius: 10px; padding: 0.6rem 1.5rem; font-weight: 600; }
    .stButton>button:hover { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(99,102,241,0.3); }
    .stCodeBlock { border-radius: 10px; margin-top: 0.5rem; }
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
    if 'selected_saved' not in st.session_state: st.session_state.selected_saved = []

    # 侧边栏导航
    with st.sidebar:
        st.markdown("<h2 style='text-align:center;color:#1E293B;margin-bottom:1.5rem;'>🗂️ AI Anki</h2>", unsafe_allow_html=True)
        pages = ["🛠️ 制作", "📜 历史记录", "💾 已保存的卡"]
        for p in pages:
            btn_class = "nav-btn active" if st.session_state.page == p.split()[-1] else "nav-btn"
            if st.button(p, key=f"nav_{p}", use_container_width=True):
                st.session_state.page = p.split()[-1]
                st.rerun()
        st.markdown("---")
        st.caption("💡 提示：刷新页面会清空数据，建议使用下方备份功能。")
        
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
                                <div>
                                    <button class="btn-action" onclick="navigator.clipboard.writeText(`{c['front'].replace('`','\\`')}`).innerText='已复制正面'; setTimeout(()=>this.innerText='复制正面',2000)">复制正面</button>
                                    <button class="btn-action" onclick="navigator.clipboard.writeText(`{c['back'].replace('`','\\`')}`).innerText='已复制背面'; setTimeout(()=>this.innerText='复制背面',2000)" style="margin-left:6px;">复制背面</button>
                                    <button class="btn-action" style="margin-left:6px;" id="save_{i}" onclick="fetch('/?save_idx={i}').then(()=>this.innerText='已保存!')">💾 保存</button>
                                </div>
                            </div>
                            <div style="font-size:0.9rem;line-height:1.6;color:#475569;white-space:pre-wrap;">{c['front']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # 导出当前批次
                if st.button("📦 导出当前批次为 .apkg", use_container_width=True):
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
                    <div>
                        <button class="btn-action" onclick="fetch('/?load_hist={idx}');setTimeout(()=>location.reload(),500)">📂 加载</button>
                        <button class="btn-action" style="margin-left:6px;" onclick="fetch('/?del_hist={idx}');setTimeout(()=>location.reload(),500)">🗑️</button>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            # 导出全部历史
            all_cards = [c for r in st.session_state.history for c in r['cards']]
            if all_cards and st.button("📦 导出全部历史记录", use_container_width=True):
                path = export_to_apkg(all_cards, "All_History")
                with open(path,"rb") as f: st.download_button("⬇️ 下载 .apkg", f, "all_history.apkg", "application/octet-stream", use_container_width=True)

    # ================= 💾 已保存的卡页面 =================
    elif st.session_state.page == '已保存的卡':
        st.markdown('<h1 class="page-title">💾 已保存的卡</h1>', unsafe_allow_html=True)
        st.markdown('<p class="page-subtitle">收藏的优质卡片库，支持多选导出</p>', unsafe_allow_html=True)
        
        if not st.session_state.saved:
            st.info("💎 暂无收藏卡片，在“制作”页面点击“保存”即可加入收藏库。")
        else:
            # 筛选器
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
                        <div style="font-size:0.85rem;line-height:1.5;color:#475569;max-height:100px;overflow:hidden;">{c['front'][:100]}...</div>
                        <div style="margin-top:0.5rem;display:flex;gap:0.5rem;">
                            <button class="btn-action" style="flex:1;" onclick="navigator.clipboard.writeText(`{c['front'].replace('`','\\`')}`)">📋 复制</button>
                            <button class="btn-action" style="flex:1;background:#FEE2E2;color:#DC2626;border-color:#FCA5A5;" onclick="fetch('/?del_saved={st.session_state.saved.index(c)}');setTimeout(()=>location.reload(),500)">🗑️ 删除</button>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # 导出选中/全部
            if display_cards and st.button("📦 导出当前筛选列表", use_container_width=True):
                path = export_to_apkg(display_cards, "Saved_Cards")
                with open(path,"rb") as f: st.download_button("⬇️ 下载 .apkg", f, "saved_cards.apkg", "application/octet-stream", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 🌐 简单路由处理 (保存/加载/删除)
    if "save_idx" in st.query_params:
        idx = int(st.query_params["save_idx"])
        if 0 <= idx < len(st.session_state.current_cards):
            st.session_state.saved.append(st.session_state.current_cards[idx])
            st.success("✅ 已添加到收藏库！")
            st.rerun()
    if "load_hist" in st.query_params:
        idx = int(st.query_params["load_hist"])
        st.session_state.current_cards = st.session_state.history[idx]['cards']
        st.session_state.page = '制作'
        st.rerun()
    if "del_hist" in st.query_params:
        idx = int(st.query_params["del_hist"])
        st.session_state.history.pop(idx)
        st.rerun()
    if "del_saved" in st.query_params:
        idx = int(st.query_params["del_saved"])
        st.session_state.saved.pop(idx)
        st.rerun()

if __name__ == "__main__":
    main()