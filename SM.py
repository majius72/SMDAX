import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="DAX Structural Analysis", page_icon="📊", layout="wide")

# --- 2. DATENGRUNDLAGE & LOGIK ---
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
                history.append({"Unternehmen": out_co, "Aufnahme": start_date, "Abstieg": date, "Status": "Ex-Konstituent", "Ersetzt_durch": nachfolger_name})
        for in_co in ins:
            active_companies[in_co] = date

    for co, start_date in active_companies.items():
        history.append({"Unternehmen": co, "Aufnahme": start_date, "Abstieg": None, "Status": "Aktueller Konstituent", "Ersetzt_durch": "N/A"})

    df = pd.DataFrame(history)
    df['Aufnahme'] = pd.to_datetime(df['Aufnahme'])
    df['Abstieg'] = pd.to_datetime(df['Abstieg'])
    
    ticker_map = {"Allianz": "ALV.DE", "BASF": "BAS.DE", "Bayer": "BAYN.DE", "BMW": "BMW.DE", "Commerzbank": "CBK.DE", "Continental": "CON.DE", "Deutsche Bank": "DBK.DE", "Deutsche Börse": "DB1.DE", "Deutsche Post": "DHL.DE", "Deutsche Telekom": "DTE.DE", "E.ON": "EOAN.DE", "Fresenius": "FRE.DE", "Fresenius Medical Care": "FME.DE", "GEA Group": "G1A.DE", "Hannover Rückversicherung": "HNR1.DE", "Henkel": "HEN3.DE", "Infineon": "IFX.DE", "Merck KGaA": "MRK.DE", "MTU Aero Engines": "MTX.DE", "Münchener Rückversicherung": "MUV2.DE", "Porsche AG": "P911.DE", "Rheinmetall AG": "RHM.DE", "RWE": "RWE.DE", "SAP": "SAP.DE", "Scout24": "G24.DE", "Siemens": "SIE.DE", "Siemens Energy AG": "ENR.DE", "Symrise AG": "SY1.DE", "Volkswagen": "VOW3.DE", "Vonovia SE": "VNA.DE"}
    df['Ticker'] = df['Unternehmen'].map(ticker_map)
    return df, succession_list

df, succession_list = load_and_process_data()

# --- 3. UI ---
st.title("📊 DAX Struktur-Analyse")
tab1, tab2, tab3 = st.tabs(["Dashboard", "Spread-Analyse", "Export"])

with tab1:
    st.subheader("Index-Konstitution")
    fig = px.timeline(df, x_start="Aufnahme", x_end="Abstieg", y="Unternehmen", color="Status")
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Spread-Analyse")
    pair_options = {p['label']: p for p in succession_list if p['alt'] in df['Unternehmen'].values and p['neu'] in df['Unternehmen'].values}
    selected = st.selectbox("Paar wählen:", list(pair_options.keys()))
    if selected:
        pair = pair_options[selected]
        # Chart-Logik... (gekürzt für Übersichtlichkeit, in deinem Code enthalten)
        st.write(f"Analyse für {pair['alt']} vs {pair['neu']}")

with tab3:
    st.subheader("Datenextraktion")
    display_df = df.copy()
    display_df['Abstieg'] = display_df['Abstieg'].dt.strftime('%d.%m.%Y').fillna("Aktuell")
    display_df['Aufnahme'] = display_df['Aufnahme'].dt.strftime('%d.%m.%Y')
    st.dataframe(display_df)
    csv = display_df.to_csv(index=False, sep=';').encode('utf-8')
    st.download_button("Download CSV", data=csv, file_name='dax_historie.csv')
