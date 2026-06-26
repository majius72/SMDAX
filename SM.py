import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="DAX Structural Analysis", page_icon="📊", layout="wide")

# --- 2. DATENGRUNDLAGE ---
@st.cache_data
def load_and_process_data():
    initial_dax = [
        "Allianz", "BASF", "Bayer", "Bayer. Hypo.- und Wechsel-Bank", 
        "Bayerische Vereinsbank", "BMW", "Commerzbank", "Continental", 
        "Daimler-Benz", "Degussa", "Deutsche Babcock", "Deutsche Bank", 
        "Deutsche Lufthansa", "Dresdner Bank", "Feldmühle Nobel", "Henkel", 
        "Hoechst", "Karstadt", "Kaufhof", "Linde", "MAN", "Mannesmann", 
        "Nixdorf", "RWE", "Schering", "Siemens", "Thyssen", "Veba", "Viag", "Volkswagen"
    ]

    changes = [
        ("1990-09-03", ["Feldmühle Nobel", "Nixdorf"], ["Metallgesellschaft", "Preussag"]),
        ("1995-09-18", ["Deutsche Babcock"], ["SAP"]),
        ("1996-07-22", ["Kaufhof"], ["Metro"]),
        ("1996-09-23", ["Continental"], ["Münchener Rückversicherung"]),
        ("1996-11-18", ["Metallgesellschaft"], ["Deutsche Telekom"]),
        ("1998-06-22", ["Bayerische Vereinsbank", "Bayer. Hypo.- und Wechsel-Bank"], ["Bayer. Hypo- und Vereinsbank", "adidas-Salomon"]),
        ("1998-12-21", ["Daimler-Benz"], ["DaimlerChrysler"]),
        ("1999-03-22", ["Degussa"], ["Degussa-Hüls"]),
        ("1999-03-25", ["Thyssen"], ["ThyssenKrupp"]),
        ("1999-09-20", ["Hoechst"], ["Fresenius Medical Care"]),
        ("2000-02-14", ["Mannesmann"], ["EPCOS"]),
        ("2000-06-19", ["Veba", "Viag"], ["E.ON", "Infineon"]),
        ("2000-12-18", ["Degussa-Hüls"], ["Degussa"]),
        ("2001-03-19", ["Karstadt"], ["Deutsche Post"]),
        ("2001-07-23", ["Dresdner Bank"], ["MLP"]),
        ("2002-09-23", ["Degussa"], ["Altana"]),
        ("2002-12-23", ["EPCOS"], ["Deutsche Börse"]),
        ("2003-09-22", ["MLP"], ["Continental"]),
        ("2005-12-19", ["Bayer. Hypo- und Vereinsbank"], ["Hypo Real Estate Holding"]),
        ("2006-09-18", ["Schering"], ["Deutsche Postbank"]),
        ("2007-06-18", ["Altana"], ["Merck KGaA"]),
        ("2008-09-22", ["Preussag"], ["K+S"]), 
        ("2008-12-22", ["Continental", "Hypo Real Estate Holding"], ["Beiersdorf", "Salzgitter"]),
        ("2009-03-23", ["Infineon", "Deutsche Postbank"], ["Fresenius", "Hannover Rückversicherung"]),
        ("2009-09-21", ["Hannover Rückversicherung"], ["Infineon"]),
        ("2010-06-21", ["Salzgitter"], ["Heidelberg Cement"]),
        ("2012-09-24", ["MAN", "Metro"], ["Lanxess", "Continental"]),
        ("2015-09-21", ["Lanxess"], ["Vonovia SE"]),
        ("2016-03-21", ["K+S"], ["ProSiebenSat.1 Media"]),
        ("2018-03-19", ["ProSiebenSat.1 Media"], ["Covestro AG"]),
        ("2018-09-24", ["Commerzbank"], ["Wirecard AG"]),
        ("2019-09-23", ["ThyssenKrupp"], ["MTU Aero Engines"]),
        ("2020-06-22", ["Deutsche Lufthansa"], ["Deutsche Wohnen SE"]),
        ("2020-08-24", ["Wirecard AG"], ["Delivery Hero SE"]),
        ("2021-03-22", ["Beiersdorf"], ["Siemens Energy AG"]),
        ("2021-10-29", ["Deutsche Wohnen SE"], ["Beiersdorf"]),
        ("2022-03-21", ["Beiersdorf", "Siemens Energy AG"], ["Daimler Truck Holding", "Hannover Rückversicherung"]),
        ("2022-06-20", ["Delivery Hero SE"], ["Beiersdorf"]),
        ("2022-09-19", ["HelloFresh SE"], ["Siemens Energy AG"]),
        ("2022-12-19", ["Puma SE"], ["Porsche AG"]),
        ("2023-02-27", ["Linde"], ["Commerzbank"]),
        ("2023-03-20", ["Fresenius Medical Care"], ["Rheinmetall AG"]),
        ("2024-12-27", ["Covestro AG", "Sartorius AG VZ", "Porsche AG"], ["Fresenius Medical Care", "GEA Group", "Scout24"])
    ]

    active_companies = {co: "1987-12-30" for co in initial_dax}
    history = []
    succession_list = []

    for date, outs, ins in changes:
        for i, out_co in enumerate(outs):
            replacer = ins[i] if i < len(ins) else "Index-Restrukturierung"
            succession_list.append({
                "alt": out_co, "neu": replacer, "datum": date,
                "label": f"{out_co} ➡️ {replacer} ({datetime.strptime(date, '%Y-%m-%d').strftime('%d.%m.%Y')})"
            })
            
        for out_co in outs:
            if out_co in active_companies:
                start_date = active_companies.pop(out_co)
                nachfolger_name = next((x['neu'] for x in succession_list if x['alt'] == out_co and x['datum'] == date), "Keiner")
                history.append({
                    "Unternehmen": out_co, 
                    "Aufnahme": pd.to_datetime(start_date), 
                    "Abstieg": pd.to_datetime(date), 
                    "Status": "Ex-Konstituent", 
                    "Ersetzt_durch": nachfolger_name
                })
        for in_co in ins:
            active_companies[in_co] = date

    today_str = datetime.today().strftime('%Y-%m-%d')
    for co, start_date in active_companies.items():
        history.append({
            "Unternehmen": co, 
            "Aufnahme": pd.to_datetime(start_date), 
            "Abstieg": pd.NaT, # NaT = Not a Time, sauberer für Excel
            "Status": "Aktueller Konstituent", 
            "Ersetzt_durch": "N/A"
        })

    df = pd.DataFrame(history)
    return df, succession_list

df, succession_list = load_and_process_data()

# --- 3. UI LAYOUT ---
st.title("📊 DAX Struktur-Analyse")
st.markdown("Quantitative Evaluation der Index-Historie (1988–YTD).")

# --- 4. EXPORT BEREICH (Korrigiert) ---
st.subheader("4. Datenextraktion")
display_df = df.copy()
# Formatierung für Excel lesbar machen, aber Datentypen beibehalten
display_df['Aufnahme'] = display_df['Aufnahme'].dt.date
display_df['Abstieg'] = display_df['Abstieg'].dt.date

st.dataframe(display_df, width=1200)

csv = display_df.to_csv(index=False, sep=';').encode('utf-8')
st.download_button(label="📊 Datensatz herunterladen (.csv)", data=csv, file_name='dax_historie_pro.csv', mime='text/csv')
