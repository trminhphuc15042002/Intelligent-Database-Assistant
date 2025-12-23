import streamlit as st 
from sqlalchemy import text
import pandas as pd
import matplotlib.pyplot as plt 
import re


# Drawing chart function
def drawing_chart(question, result):
    session = st.session_state.SessionLocal()
    return_result = session.execute(text(result["sql_query"]))
    all_results = return_result.fetchall()
    session.close()

    if not all_results:
        return None

    labels, values = zip(*all_results)

    fig, ax = plt.subplots(figsize=(10, 6))

    if len(all_results) > 10:
        df = pd.DataFrame(all_results, columns=["Column 1", "Column 2"])
        df = df.sort_values(by="Column 2", ascending=True).tail(10)
        ax.barh(df["Column 1"], df["Column 2"])
    elif "top" in question.lower():
        top_n = 10
        match = re.search(r'\d+', question)
        top_n = int(match.group()) if match else 10
        df = pd.DataFrame(all_results, columns=["Column 1", "Column 2"])
        df = df.sort_values(by="Column 2", ascending=True).tail(top_n)
        ax.barh(df["Column 1"], df["Column 2"])
    elif 6 < len(all_results) <= 10:
        ax.bar(labels, values)
        plt.xticks(rotation=45)
    else:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        ax1.bar(labels, values)
        ax1.set_xticklabels(labels, rotation=45)
        ax2.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        ax2.axis('equal')
        plt.tight_layout()
        return fig

    plt.tight_layout()
    return fig