import streamlit as st
from shared_data import MODULES_4

st.title("Parents Portal — 4 Intervention & Training Modules")
st.caption("Practical home routines and guides across four core areas.")

cols = st.columns(2, gap="large")
for idx, mod in enumerate(MODULES_4):
    with cols[idx % 2]:
        with st.container(border=True):
            st.markdown(f"### {mod['code']}: {mod['title']}")
            st.caption(f"Focus Area: {mod['domain']}")
            st.text(mod["steps"])
            guide_bytes = f"{mod['code']} - {mod['title']}\nFocus: {mod['domain']}\n\n{mod['steps']}\n".encode("utf-8")
            st.download_button(
                label=f"Download {mod['code']} Guide",
                data=guide_bytes,
                file_name=f"{mod['code'].replace(' ', '_')}.txt",
                mime="text/plain",
                key=f"mod_dl_{idx}",
            )
