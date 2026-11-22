import pandas as pd
import streamlit as st
from shared_data import init_state

df_students = init_state()

st.title("Admin — Required Services & Age Distribution Graphs")

s1, s2 = st.columns(2, gap="large")
with s1:
    st.subheader("Required Service by District")
    st.bar_chart(pd.crosstab(df_students["District"], df_students["Required Service"]), height=340)

with s2:
    st.subheader("Student Count by Age")
    st.bar_chart(df_students.groupby("Age").size().rename("Students"), height=340)

st.divider()
st.subheader("Diagnosis vs. Required Service Table")
st.dataframe(pd.crosstab(df_students["Diagnosis"], df_students["Required Service"]), use_container_width=True)
