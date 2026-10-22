import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="VCM Műszeres Műszaknapló", page_icon="🔧", layout="wide")

@st.cache_data
def load_data():
    filepath = 'VCM Üzem - Műszeres preventív karbantartás 2026.10.12.xlsx'
    if not os.path.exists(filepath):
        return None, None, None
    
    df_szab = pd.read_excel(filepath, sheet_name='Szabályzószelepek', skiprows=1)
    df_nyz = pd.read_excel(filepath, sheet_name='Nyit-zár szelepek', skiprows=1)
    df_mero = pd.read_excel(filepath, sheet_name='Mérőműszerek', skiprows=1)
    
    instruments = []
    for _, r in df_szab.iterrows():
        poz = str(r.iloc[1]).strip() if pd.notna(r.iloc[1]) else ""
        if not poz or poz.lower() in ["nan", "s.sz."]: continue
        instruments.append({"Pozíciószám": poz, "Főkategória": "Szabályzószelep", "Típus": str(r.iloc[3]), "Blokk": str(r.iloc[4]), "Tech. berendezés": str(r.iloc[6]), "Funkció": str(r.iloc[7]), "Gyártó": str(r.iloc[17]), "Gyári szám": str(r.iloc[19]), "Karima méret": str(r.iloc[21]), "Mérési elv": "", "Állványzat": str(r.iloc[22])})
        
    for _, r in df_nyz.iterrows():
        poz = str(r.iloc[1]).strip() if pd.notna(r.iloc[1]) else ""
        if not poz or poz.lower() in ["nan", "s.sz."]: continue
        instruments.append({"Pozíciószám": poz, "Főkategória": "Nyit-zár szelep", "Típus": str(r.iloc[3]), "Blokk": str(r.iloc[4]), "Tech. berendezés": str(r.iloc[6]), "Funkció": str(r.iloc[7]), "Gyártó": str(r.iloc[16]), "Gyári szám": "", "Karima méret": "", "Mérési elv": "", "Állványzat": str(r.iloc[19])})

    for _, r in df_mero.iterrows():
        poz = str(r.iloc[1]).strip() if pd.notna(r.iloc[1]) else ""
        if not poz or poz.lower() in ["nan", "s.sz."]: continue
        instruments.append({"Pozíciószám": poz, "Főkategória": "Mérőműszer / Kapcsoló", "Típus": str(r.iloc[3]), "Blokk": str(r.iloc[4]), "Tech. berendezés": str(r.iloc[6]), "Funkció": str(r.iloc[7]), "Gyártó": str(r.iloc[16]), "Gyári szám": "", "Karima méret": "", "Mérési elv": str(r.iloc[18]), "Állványzat": str(r.iloc[19])})
        
    df_inst = pd.DataFrame(instruments)
    users = {
        "dtheisz": {"name": "Theisz Dániel", "pass": "admin123", "role": "Műszakvezető"},
        "muszeresz1": {"name": "Kovács Péter", "pass": "1234", "role": "Műszerész"}
    }
    lists = {
        "beavatkozas": ["Hibaelhárítás / Javítás", "Preventív karbantartás (H-PK)", "Preventív karbantartás (M-PK)", "Kalibrálás", "Diagnosztika (DI)"],
        "muszakok": [
            "8 órás állandó délelőttös műszak (06:00 - 14:00)",
            "12 órás nappalos műszak (06:00 - 18:00)",
            "12 órás éjszakás műszak (18:00 - 06:00)"
        ]
    }
    return df_inst, users, lists

df_inst, users, lists = load_data()

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'logs' not in st.session_state: st.session_state['logs'] = pd.DataFrame(columns=["ID", "Dátum", "Műszak", "Pozíciószám", "Típus", "Beavatkozás", "Leírás", "Vezető javító", "Segítő"])
if 'db' not in st.session_state: st.session_state['db'] = df_inst

if not st.session_state['logged_in']:
    st.title("🔧 VCM Üzem - Műszeres Műszaknapló")
    u = st.text_input("Felhasználónév (dtheisz vagy muszeresz1)")
    p = st.text_input("Jelszó", type="password")
    if st.button("Belépés", type="primary"):
        if u in users and users[u]["pass"] == p:
            st.session_state['logged_in'] = True
            st.session_state['fullname'] = users[u]["name"]
            st.session_state['role'] = users[u]["role"]
            st.rerun()
        else:
            st.error("Hibás adatok!")
    st.stop()

st.sidebar.write(f"**Név:** {st.session_state['fullname']}")
st.sidebar.write(f"**Jogosultság:** {st.session_state['role']}")
if st.sidebar.button("Kijelentkezés"):
    st.session_state['logged_in'] = False
    st.rerun()

st.title("📋 VCM Üzem - Műszeres Műszaknapló & Adatbázis")
tab1, tab2, tab3 = st.tabs(["🛠️ Műszer Keresés & Naplózás", "📊 Műszer Törzsadatbázis", "📜 Előzmények"])

with tab1:
    search_poz = st.text_input("Pozíciószám keresése (pl. FV12334, FT111):", "").strip().upper()
    db = st.session_state['db']
    inst_row = db[db['Pozíciószám'] == search_poz] if search_poz else pd.DataFrame()
    
    if not inst_row.empty:
        r = inst_row.iloc[0]
        f_kat, f_tipus, f_blokk, f_tech, f_funk, f_gyarto, f_sn, f_karima, f_elv, f_allv = r['Főkategória'], r['Típus'], r['Blokk'], r['Tech. berendezés'], r['Funkció'], r['Gyártó'], r['Gyári szám'], r['Karima méret'], r['Mérési elv'], r['Állványzat']
        st.success(f"Meglévő műszer betöltve: {search_poz}")
    else:
        if search_poz: st.warning("Új műszer! Töltsd ki az adatait.")
        f_kat, f_tipus, f_blokk, f_tech, f_funk, f_gyarto, f_sn, f_karima, f_elv, f_allv = "Szabályzószelep", "Áramlásmérő", "", "", "", "", "", "", "", ""

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### Törzsadatok")
        c_kat = st.selectbox("Főkategória", ["Szabályzószelep", "Nyit-zár szelep", "Mérőműszer / Kapcsoló"])
        c_tipus = st.text_input("Típus", value=f_tipus)
        c_blokk = st.text_input("Szekció / Blokk", value=f_blokk)
        c_tech = st.text_input("Tech. berendezés", value=f_tech)
        c_funk = st.text_input("Funkció", value=f_funk)
        c_gyarto = st.text_input("Gyártó", value=f_gyarto)
        c_sn = st.text_input("Gyári szám", value=f_sn)
        c_karima = st.text_input("Karima méret", value=f_karima)
        c_elv = st.text_input("Mérési elv", value=f_elv)
        c_allv = st.text_input("Állványzat", value=f_allv)
    with c2:
        st.markdown("### Műszaknapló Bejegyzés")
        w_date = st.text_input("Dátum", value=datetime.now().strftime("%Y-%m-%d"))
        w_shift = st.selectbox("Műszak", lists["muszakok"])
        other_users = [u["name"] for u in users.values() if u["name"] != st.session_state['fullname']]
        w_helper = st.selectbox("Segítő kolléga", ["- (Egyedül végezte)"] + other_users)
        w_action = st.selectbox("Beavatkozás jellege", lists["beavatkozas"])
        w_desc = st.text_area("Elvégzett munka részletes leírása [*]:", height=130)
        
        if st.button("💾 Mentés", type="primary", use_container_width=True):
            if not search_poz or not w_desc:
                st.error("Add meg a pozíciószámot és a leírást!")
            else:
                if not inst_row.empty:
                    idx = inst_row.index[0]
                    st.session_state['db'].loc[idx, ['Típus', 'Blokk', 'Tech. berendezés', 'Funkció', 'Gyártó', 'Gyári szám', 'Karima méret', 'Mérési elv', 'Állványzat']] = [c_tipus, c_blokk, c_tech, c_funk, c_gyarto, c_sn, c_karima, c_elv, c_allv]
                else:
                    new_i = pd.DataFrame([{"Pozíciószám": search_poz, "Főkategória": c_kat, "Típus": c_tipus, "Blokk": c_blokk, "Tech. berendezés": c_tech, "Funkció": c_funk, "Gyártó": c_gyarto, "Gyári szám": c_sn, "Karima méret": c_karima, "Mérési elv": c_elv, "Állványzat": c_allv}])
                    st.session_state['db'] = pd.concat([st.session_state['db'], new_i], ignore_index=True)
                
                new_l = pd.DataFrame([{"ID": len(st.session_state['logs'])+1, "Dátum": w_date, "Műszak": w_shift, "Pozíciószám": search_poz, "Típus": c_tipus, "Beavatkozás": w_action, "Leírás": w_desc, "Vezető javító": st.session_state['fullname'], "Segítő": "" if w_helper=="- (Egyedül végezte)" else w_helper}])
                st.session_state['logs'] = pd.concat([new_l, st.session_state['logs']], ignore_index=True)
                st.success("Sikeres mentés!")

with tab2:
    st.dataframe(st.session_state['db'], use_container_width=True, height=450)
with tab3:
    st.dataframe(st.session_state['logs'], use_container_width=True, height=450)