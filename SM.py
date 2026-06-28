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
def fetch_dax_history():
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
        
        # --- HISTORISCH KORREKTE TRENNUNG 2024 / 2025 ---
        ("2024-12-27", ["Covestro AG"], ["Fresenius Medical Care"]),
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
    
    sort_order = df.groupby('Unternehmen').agg({'Primary_Slot': 'min', 'Aufnahme': 'min'}).sort_values(by=['Primary_Slot', 'Aufnahme'])
    ordered_companies = sort_order.index.tolist()

    return df, succession_list, ordered_companies

df, succession_list, ordered_companies = fetch_dax_history()

# --- 3. HEADER & KPIs ---
st.title("📊 DAX Struktur-Analyse")
st.markdown("**Quantitative Evaluation der DAX-Zusammensetzung (1988–YTD).** Analyse von Substitutions-Effekten und Evaluation des strukturellen Performance-Drags durch passive Index-Replikation.")

total_absteiger = len(df[df['Status'] == 'Ex-Konstituent'])
aktuelle_mitglieder = len(df[df['Status'] == 'Aktueller Konstituent'])
c1, c2, c3 = st.columns(3)
c1.metric("Historische Index-Austritte", f"{total_absteiger} Konstituenten")
c2.metric("Aktuelle Index-Mitglieder", f"{aktuelle_mitglieder} (DAX 40)")
c3.metric("Struktureller Drag-Faktor", "Nachweisbar negativ")
st.divider()

# --- 4. BEREICH 1: INDEX-KONSTITUTION (KASKADIERT & HOVER-DATEN) ---
st.subheader("1. Index-Konstitution & Fluktuation (Substitutions-Ketten)")
st.markdown("Visuelle Darstellung der Index-Verweildauer. Unterbrechungen im Balken markieren Phasen außerhalb des Index. Die Y-Achse ist so sortiert, dass direkte Nachfolger treppenartig untereinander erscheinen.")

df['Hover_Aufnahme'] = df['Aufnahme'].dt.strftime('%d.%m.%Y')
df['Hover_Abstieg'] = df.apply(lambda row: "Heute" if row['Status'] == 'Aktueller Konstituent' else row['Abstieg'].strftime('%d.%m.%Y'), axis=1)

fig_timeline = px.timeline(
    df, 
    x_start="Aufnahme", 
    x_end="Abstieg", 
    y="Unternehmen", 
    color="Status",
    custom_data=["Ersetzt_durch", "Status", "Hover_Aufnahme", "Hover_Abstieg"], 
    color_discrete_map={"Aktueller Konstituent": "#1f77b4", "Ex-Konstituent": "#d62728"},
    height=1600 
)

fig_timeline.update_yaxes(categoryorder="array", categoryarray=ordered_companies, autorange="reversed", title="Index-Konstituent")
fig_timeline.update_traces(
    hovertemplate="<b>%{y}</b><br><br>Zeitraum: %{customdata[2]} – %{customdata[3]}<br>Status: %{customdata[1]}<br>Substitution durch: %{customdata[0]}<extra></extra>"
)
st.plotly_chart(fig_timeline, use_container_width=True)
st.divider()

# --- 5. BEREICH 2: SPREAD-ANALYSE ---
st.subheader("2. Spread-Analyse: Substitutions-Effekte")
ticker_vorhanden = df[df['Ticker'].notna()]['Unternehmen'].values
valide_paere = [p for p in succession_list if p['alt'] in ticker_vorhanden and p['neu'] in ticker_vorhanden]
pair_options = {p['label']: p for p in valide_paere}

if valide_paere:
    selected_pair_label = st.selectbox("Index-Restrukturierung auswählen:", list(pair_options.keys()), index=None, placeholder="Bitte ein Wechsel-Szenario wählen...")
    if selected_pair_label:
        pair = pair_options[selected_pair_label]
        alt_co, neu_co, wechsel_datum = pair['alt'], pair['neu'], pair['datum']
        wechsel_datum_str = datetime.strptime(wechsel_datum, '%Y-%m-%d').strftime('%d.%m.%Y')
        ticker_alt = df[df['Unternehmen'] == alt_co]['Ticker'].values[0]
        ticker_neu = df[df['Unternehmen'] == neu_co]['Ticker'].values[0]
        
        try:
            data_alt = yf.Ticker(ticker_alt).history(start=wechsel_datum, end=datetime.today().strftime('%Y-%m-%d'))
            data_neu = yf.Ticker(ticker_neu).history(start=wechsel_datum, end=datetime.today().strftime('%Y-%m-%d'))
            
            if not data_alt.empty and not data_neu.empty:
                start_alt = data_alt['Close'].iloc[0]
                start_neu = data_neu['Close'].iloc[0]
                data_alt['Indexed'] = (data_alt['Close'] / start_alt) * 100
                data_neu['Indexed'] = (data_neu['Close'] / start_neu) * 100
                
                perf_alt = ((data_alt['Close'].iloc[-1] - start_alt) / start_alt) * 100
                perf_neu = ((data_neu['Close'].iloc[-1] - start_neu) / start_neu) * 100
                
                col1, col2 = st.columns(2)
                col1.metric(f"Absteiger: {alt_co}", f"{perf_alt:.2f} %", delta=f"{perf_alt:.2f} % (seit {wechsel_datum_str})")
                col2.metric(f"Aufsteiger: {neu_co}", f"{perf_neu:.2f} %", delta=f"{perf_neu:.2f} % (seit {wechsel_datum_str})")
                
                fig_duell = go.Figure()
                fig_duell.add_trace(go.Scatter(x=data_alt.index, y=data_alt['Indexed'], name=f"Absteiger: {alt_co}", line=dict(color='#d62728', width=2.5)))
                fig_duell.add_trace(go.Scatter(x=data_neu.index, y=data_neu['Indexed'], name=f"Aufsteiger: {neu_co}", line=dict(color='#2ca02c', width=2.5)))
                st.plotly_chart(fig_duell, use_container_width=True)
            else:
                st.warning("Keine ausreichenden historischen Kursdaten für dieses Pärchen verfügbar.")
        except Exception as e:
            st.error("Fehler beim Abruf der Kursdaten. Bitte später erneut versuchen.")

st.divider()

# --- 6. BEREICH 3: ZEITREIHEN-ANALYSE ---
st.subheader("3. Historische Zeitreihenanalyse")
selected_co = st.selectbox("Konstituent auswählen:", sorted(df[df['Ticker'].notna()]['Unternehmen'].unique()), index=None, placeholder="Unternehmen wählen...")
if selected_co:
    ticker_co = df[df['Unternehmen'] == selected_co]['Ticker'].values[0]
    try:
        hist_free = yf.Ticker(ticker_co).history(start="1990-01-01", end=datetime.today().strftime('%Y-%m-%d'))
        if not hist_free.empty:
            st.line_chart(hist_free['Close'], use_container_width=True)
    except Exception:
        st.error("Laden der Daten nicht möglich.")

st.divider()

# --- 7. BEREICH 4: STATISTISCHE EVIDENZ (NEU) ---
st.subheader("4. Statistische Evidenz: Der Vorlauf-Drag (Pre-Swap Analysis)")
st.markdown("Diese Analyse prüft die Kernhypothese mathematisch: **Kostet die reaktive Natur des Index Rendite?** Wir betrachten exakt das **Jahr vor dem Indexwechsel** (T-365 Tage bis zum Wechseltag). Wir vergleichen, wie stark der Absteiger das Index-Portfolio in dieser Zeit belastet hat, während der Aufsteiger außerhalb des Index rasant gewachsen ist.")

if valide_paere:
    if st.button("🧮 Opportunitätskosten für das Jahr vor dem Wechsel berechnen"):
        with st.spinner("Berechne historische Rendite-Deltas (12 Monate vor Index-Austritt)..."):
            results = []
            
            for p in valide_paere:
                wechsel_datum = datetime.strptime(p['datum'], '%Y-%m-%d')
                # 1 Jahr vor dem Rauswurf
                start_datum = wechsel_datum - pd.DateOffset(years=1)
                
                ticker_a = df[df['Unternehmen'] == p['alt']]['Ticker'].values[0]
                ticker_n = df[df['Unternehmen'] == p['neu']]['Ticker'].values[0]
                
                try:
                    data_a = yf.Ticker(ticker_a).history(start=start_datum.strftime('%Y-%m-%d'), end=wechsel_datum.strftime('%Y-%m-%d'))
                    data_n = yf.Ticker(ticker_n).history(start=start_datum.strftime('%Y-%m-%d'), end=wechsel_datum.strftime('%Y-%m-%d'))
                    
                    if not data_a.empty and not data_n.empty and len(data_a) > 50 and len(data_n) > 50:
                        start_a, end_a = data_a['Close'].iloc[0], data_a['Close'].iloc[-1]
                        start_n, end_n = data_n['Close'].iloc[0], data_n['Close'].iloc[-1]
                        
                        perf_a = ((end_a - start_a) / start_a) * 100
                        perf_n = ((end_n - start_n) / start_n) * 100
                        delta = perf_n - perf_a
                        
                        # Plausibilitätsfilter: Schließt offensichtliche Yahoo-Datenfehler (z.B. >500% in einem Jahr durch unbereinigte Splits) aus
                        if abs(delta) < 500:
                            results.append({
                                "Paar": f"{p['alt']} ➡️ {p['neu']} ({wechsel_datum.year})",
                                "Delta": delta,
                                "Sieger": "Aufsteiger im Vorfeld besser" if delta > 0 else "Absteiger im Vorfeld besser",
                                "Aufsteiger_Perf": perf_n,
                                "Absteiger_Perf": perf_a
                            })
                except Exception:
                    continue 
            
            if results:
                res_df = pd.DataFrame(results)
                
                # --- METRIKEN BERECHNEN ---
                hit_rate = (len(res_df[res_df['Delta'] > 0]) / len(res_df)) * 100
                avg_delta = res_df['Delta'].mean()
                median_delta = res_df['Delta'].median()
                
                st.markdown("### 📊 Opportunitätskosten (12 Monate vor dem Rauswurf)")
                col_m1, col_m2, col_m3 = st.columns(3)
                col_m1.metric("Aufsteiger Outperformance-Quote", f"{hit_rate:.1f} %", "Fälle mit positiver Rendite-Schere")
                col_m2.metric("Ø Verpasste Rendite (Mean)", f"+ {avg_delta:.1f} %", "Durchschnittliches Delta")
                col_m3.metric("Median Verpasste Rendite", f"+ {median_delta:.1f} %", "Robuste Schätzung")
                
                # --- VISUALISIERUNG ---
                res_df = res_df.sort_values('Delta', ascending=True)
                fig_bar = px.bar(
                    res_df, 
                    x="Delta", 
                    y="Paar", 
                    orientation='h',
                    color="Sieger",
                    color_discrete_map={"Aufsteiger im Vorfeld besser": "#2ca02c", "Absteiger im Vorfeld besser": "#d62728"},
                    title="Verpasste Rendite pro Wechsel (Aufsteiger minus Absteiger im Vorjahr)",
                    height=max(400, len(res_df)*35),
                    custom_data=["Aufsteiger_Perf", "Absteiger_Perf"]
                )
                fig_bar.update_layout(xaxis_title="Performance-Delta in Prozentpunkten", yaxis_title="")
                fig_bar.update_traces(
                    hovertemplate="<b>%{y}</b><br>Delta: %{x:.1f} Prozentpunkte<br>Performance Aufsteiger (außerhalb DAX): %{customdata[0]:.1f}%<br>Performance Absteiger (im DAX gehalten): %{customdata[1]:.1f}%<extra></extra>"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
                st.info("**Interpretation:** Grüne Balken bedeuten: Der Aufsteiger hat den Absteiger im Jahr **bevor** der DAX reagiert hat, massiv geschlagen. Ein passiver DAX-Anleger musste die Verluste des Absteigers voll mitnehmen, während die Gewinne des Aufsteigers nicht im Index abgebildet wurden. Das quantifiziert den strukturellen Performance-Drag durch die passive, verspätete Index-Replikation.")
            else:
                st.warning("Nicht genug validierte Daten für diese Berechnung gefunden.")
# --- 7. EXPORT ---
st.subheader("5. Datenextraktion & CSV-Export")
display_df = df.copy()
display_df = display_df.drop(columns=['Slot_ID', 'Primary_Slot', 'Hover_Aufnahme', 'Hover_Abstieg'], errors='ignore')
display_df['Abstieg'] = display_df.apply(lambda row: "Aktuell im Index" if row['Status'] == 'Aktueller Konstituent' else row['Abstieg'].strftime('%d.%m.%Y'), axis=1)
display_df['Aufnahme'] = display_df['Aufnahme'].dt.strftime('%d.%m.%Y')
st.dataframe(display_df, use_container_width=True)
csv = display_df.to_csv(index=False, sep=';').encode('utf-8')
st.download_button(label="📊 Datensatz herunterladen (.csv)", data=csv, file_name='dax_historie_pro.csv', mime='text/csv')
