import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="DAX Structural Analysis", page_icon="📊", layout="wide")

# --- 2. DATENGRUNDLAGE & HYBRID-LOGIK ---
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
        ("2021-09-20", [], ["Airbus SE", "Brenntag SE", "Qiagen NV", "Porsche Automobile Holding", "Sartorius AG VZ", "Symrise AG", "Zalando SE"]),
        ("2021-10-29", ["Deutsche Wohnen SE"], ["Beiersdorf"]),
        ("2022-03-21", ["Beiersdorf", "Siemens Energy AG"], ["Daimler Truck Holding", "Hannover Rückversicherung"]),
        ("2022-06-20", ["Delivery Hero SE"], ["Beiersdorf"]),
        ("2022-09-19", ["HelloFresh SE"], ["Siemens Energy AG"]),
        ("2022-12-19", ["Puma SE"], ["Porsche AG"]),
        ("2023-02-27", ["Linde"], ["Commerzbank"]),
        ("2023-03-20", ["Fresenius Medical Care"], ["Rheinmetall AG"]),
        ("2024-03-18", ["Covestro AG"], ["Fresenius Medical Care"]), 
        ("2025-09-22", ["Porsche AG", "Sartorius AG VZ"], ["GEA Group", "Scout24"])
    ]

    active_companies = {co: "1987-12-30" for co in initial_dax}
    current_slots = {co: i for i, co in enumerate(initial_dax, 1)}
    next_new_slot = 31 
    history = []
    succession_list = []

    for date, outs, ins in changes:
        for i, out_co in enumerate(outs):
            replacer = ins[i] if i < len(ins) else "Index-Restrukturierung"
            succession_list.append({
                "alt": out_co, "neu": replacer, "datum": date,
                "label": f"{out_co} ➡️ {replacer} ({datetime.strptime(date, '%Y-%m-%d').strftime('%d.%m.%Y')})"
            })
            
        for i, out_co in enumerate(outs):
            if out_co in active_companies:
                start_date = active_companies.pop(out_co)
                slot_id = current_slots.pop(out_co, next_new_slot)
                nachfolger_name = next((x['neu'] for x in succession_list if x['alt'] == out_co and x['datum'] == date), "Keiner")
                
                history.append({
                    "Unternehmen": out_co, "Aufnahme": start_date, "Abstieg": date, 
                    "Status": "Ex-Konstituent", "Ersetzt_durch": nachfolger_name,
                    "Slot_ID": slot_id 
                })
                
                if i < len(ins):
                    in_co = ins[i]
                    current_slots[in_co] = slot_id
                    active_companies[in_co] = date
                    
        for i, in_co in enumerate(ins):
            if in_co not in active_companies:
                active_companies[in_co] = date
                current_slots[in_co] = next_new_slot
                next_new_slot += 1

    today_str = datetime.today().strftime('%Y-%m-%d')
    for co, start_date in active_companies.items():
        slot_id = current_slots.get(co, 99)
        history.append({
            "Unternehmen": co, "Aufnahme": start_date, "Abstieg": today_str, 
            "Status": "Aktueller Konstituent", "Ersetzt_durch": "N/A",
            "Slot_ID": slot_id
        })

    df = pd.DataFrame(history)
    df['Aufnahme'] = pd.to_datetime(df['Aufnahme'])
    df['Abstieg'] = pd.to_datetime(df['Abstieg'])
    
    ticker_map = {
        "Adidas-Salomon": "ADS.DE", "adidas-Salomon": "ADS.DE", "Airbus SE": "AIR.DE", "Allianz": "ALV.DE", 
        "BASF": "BAS.DE", "Bayer": "BAYN.DE", "Beiersdorf": "BEI.DE", "BMW": "BMW.DE", "Brenntag SE": "BNR.DE", 
        "Commerzbank": "CBK.DE", "Continental": "CON.DE", "Covestro AG": "1COV.DE", "Daimler Truck Holding": "DTG.DE", 
        "Delivery Hero SE": "DHER.DE", "Deutsche Bank": "DBK.DE", "Deutsche Börse": "DB1.DE", "Deutsche Lufthansa": "LHA.DE", 
        "Deutsche Post": "DHL.DE", "Deutsche Telekom": "DTE.DE", "Deutsche Wohnen SE": "DWNI.DE", "E.ON": "EOAN.DE", 
        "Fresenius": "FRE.DE", "Fresenius Medical Care": "FME.DE", "GEA Group": "G1A.DE", "Hannover Rückversicherung": "HNR1.DE", 
        "Heidelberg Cement": "HEI.DE", "HelloFresh SE": "HFG.DE", "Henkel": "HEN3.DE", "Infineon": "IFX.DE", 
        "K+S": "SDF.DE", "Lanxess": "LXS.DE", "Linde": "LIN.DE", "MAN": "MAN.DE", "Merck KGaA": "MRK.DE", 
        "Metro": "B4B.DE", "MTU Aero Engines": "MTX.DE", "Münchener Rückversicherung": "MUV2.DE", 
        "Porsche Automobile Holding": "PAH3.DE", "Porsche AG": "P911.DE", "ProSiebenSat.1 Media": "PSM.DE", 
        "Puma SE": "PUM.DE", "Qiagen NV": "QIA.DE", "Rheinmetall AG": "RHM.DE", "RWE": "RWE.DE", "SAP": "SAP.DE", 
        "Sartorius AG VZ": "SRT.DE", "Scout24": "G24.DE", "Siemens": "SIE.DE", "Siemens Energy AG": "ENR.DE", 
        "Siemens Healthineers AG": "SHL.DE", "Symrise AG": "SY1.DE", "ThyssenKrupp": "TKA.DE", "Volkswagen": "VOW3.DE", 
        "Vonovia SE": "VNA.DE", "Wirecard AG": "WDI.DE", "Zalando SE": "ZAL.DE"
    }
    df['Ticker'] = df['Unternehmen'].map(ticker_map)

    first_slots = df.groupby('Unternehmen')['Slot_ID'].min()
    df['Primary_Slot'] = df['Unternehmen'].map(first_slots)
    
    sort_order = df.groupby('Unternehmen').agg({'Primary_Slot': 'min', 'Aufnahme': 'min'}).sort_values
