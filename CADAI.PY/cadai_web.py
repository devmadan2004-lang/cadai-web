import streamlit as st
import pandas as pd
from io import BytesIO

# ================== SESSION INIT ==================
if "stage" not in st.session_state: st.session_state.stage="select_roller"
if "costings" not in st.session_state: st.session_state.costings=[]
if "frame_costings" not in st.session_state: st.session_state.frame_costings=[]
if "constants" not in st.session_state: st.session_state.constants={}
if "selected_roller" not in st.session_state: st.session_state.selected_roller=None
if "last_roller_weight" not in st.session_state: st.session_state.last_roller_weight=0
if "qty_type" not in st.session_state: st.session_state.qty_type="Single Roller"
if "qty_value" not in st.session_state: st.session_state.qty_value=1


# ================== CONSTANTS ==================
DEFAULT_CONSTANTS = {
    "STEEL_COST": 70.0,
    "BEARING_COST_PAIR": 100.0,
    "SEAL_COST": 30.0,
    "WELDING_COST": 80.0,
    "MARKUP": 1.25,
    "FRAME_RATE": 100.0,
    "GUIDE_ROLLER": 0.0,
    "PIVOT_BEARING": 0.0,
    "LOCKING_RING": 0.0,
}


# ================== HELPERS ==================
def make_df(rows=None):

    cols = ["DESCRIPTION","SECTION","SIZE","WT/M","LENGTH","QTY","TOTAL WT"]

    if not rows:
        return pd.DataFrame(columns=cols)

    return pd.DataFrame(rows, columns=cols)


def safe_get(table, key, label):

    if key not in table:
        st.error(f"{label} not available for {key} mm")
        st.stop()

    return table[key]


# ================== FRAME WEIGHT TABLES ==================
CARRYING_FRAME_WT = {650:12.7,800:16.8,1000:23.1,1200:26.2,1400:35,1600:38.4,1800:52.4,2000:64.7}
SARI_FRAME_WT     = {650:14.2,800:18.1,1000:24.5,1200:28.9,1400:37.4,1600:41.8,1800:56.2,2000:68.9}
SARI_N_FRAME_WT   = {800:19.3,1000:26.1,1200:30.2}
SACI_FRAME_WT     = {650:13.5,800:17.2,1000:22.9,1200:27.4,1400:36.2,1600:40.5,1800:54.3,2000:66.1}


# ================== ROLLER WT → BW ==================
ROLLER_WT_TO_BW = [
    (0,15,650),(15,22,800),(22,30,1000),(30,38,1200),
    (38,48,1400),(48,60,1600),(60,75,1800),(75,1000,2000)
]

def get_bw(wt):

    for low,high,bw in ROLLER_WT_TO_BW:
        if low<=wt<high:
            return bw

    return 1000


# ================== FABRICATION TABLES ==================
# ================== FABRICATION TABLES ==================
# NOTE: Keep your dict names consistent:
# - SACI_FAB (not SACI)
# - SARI_N_FAB must NOT be overwritten later

CARRYING_FAB = {
    650: make_df([
        ["BASE ANGLE","ANGLE","65x65x6",5.8,0.984,1,5.71],
        ["SIDE BRACKET","FLAT","65x6",3.1,0.345,2,2.14],
        ["CENTER BRACKET","FLAT","65x6",3.1,0.365,2,2.26],
        ["MID FLAT","FLAT","50x6",2.4,0.300,2,1.44],
        ["BASE FLAT","FLAT","50x6",2.4,0.240,2,1.15],
    ]),
    800: make_df([
        ["BASE ANGLE","ANGLE","75x75x6",6.8,1.134,1,7.71],
        ["SIDE BRACKET","FLAT","75x6",3.5,0.385,2,2.70],
        ["CENTER BRACKET","FLAT","75x6",3.5,0.400,2,2.80],
        ["MID FLAT","FLAT","50x6",2.4,0.500,2,2.40],
        ["BASE FLAT","FLAT","50x6",2.4,0.240,2,1.15],
    ]),
    1000: make_df([
        ["BASE ANGLE","ANGLE","90x90x6",6.0,1.350,1,8.10],
        ["SIDE BRACKET","FLAT","75x8",4.7,0.425,2,4.00],
        ["CENTER BRACKET","FLAT","75x8",4.7,0.415,2,3.90],
        ["MID FLAT","FLAT","50x6",2.4,0.550,2,2.64],
        ["BASE FLAT","FLAT","65x6",3.1,0.240,2,1.49],
    ]),
    1200: make_df([
        ["BASE ANGLE","ANGLE","90x90x6",8.2,1.550,1,12.71],
        ["SIDE BRACKET","FLAT","75x8",4.7,0.485,2,4.56],
        ["CENTER BRACKET","FLAT","75x8",4.7,0.435,2,4.09],
        ["MID FLAT","FLAT","50x6",2.4,0.600,2,2.88],
        ["BASE FLAT","FLAT","65x8",4.1,0.240,2,1.97],
    ]),
    1400: make_df([
        ["BASE ANGLE","ANGLE","100x100x8",12.1,1.750,1,21.18],
        ["SIDE BRACKET","FLAT","75x8",4.7,0.520,2,4.89],
        ["CENTER BRACKET","FLAT","75x8",4.7,0.440,2,4.14],
        ["MID FLAT","FLAT","50x6",2.4,0.600,2,2.88],
        ["BASE FLAT","FLAT","65x8",4.1,0.240,2,1.97],
    ]),
    1600: make_df([
        ["BASE ANGLE","ANGLE","100x100x8",12.1,1.960,1,23.72],
        ["SIDE BRACKET","FLAT","75x8",4.7,0.560,2,5.26],
        ["CENTER BRACKET","FLAT","75x8",4.7,0.440,2,4.14],
        ["MID FLAT","FLAT","50x6",2.4,0.700,2,3.36],
        ["BASE FLAT","FLAT","65x8",4.1,0.240,2,1.97],
    ]),
    1800: make_df([
        ["BASE ANGLE","ANGLE","110x110x10",16.5,2.170,1,35.81],
        ["SIDE BRACKET","FLAT","75x8",4.7,0.610,2,5.73],
        ["CENTER BRACKET","FLAT","75x8",4.7,0.445,2,4.18],
        ["MID FLAT","FLAT","50x6",2.4,0.750,2,3.60],
        ["BASE FLAT","FLAT","75x10",5.9,0.260,2,3.07],
    ]),
    2000: make_df([
        ["BASE ANGLE","ANGLE","130x130x10",19.7,2.370,1,46.69],
        ["SIDE BRACKET","FLAT","75x8",4.7,0.650,2,6.11],
        ["CENTER BRACKET","FLAT","75x8",4.7,0.485,2,4.56],
        ["MID FLAT","FLAT","50x6",2.4,0.800,2,3.84],
        ["BASE FLAT","FLAT","75x10",5.9,0.300,2,3.54],
    ]),
}

# ✅ IMPORTANT: name must be SACI_FAB (your frame stage uses SACI_FAB)
SACI_FAB = {
    650: make_df([
        ["BASE CHANNEL", "CHANNEL", "ISMC 100 x 50", 9.2, 0.834, 1, 7.67],
        ["BRG. ANGLE", "ANGLE", "65 x 65 x 6", 5.8, 1.095, 1, 6.35],
        ["SIDE BRACKET", "FLAT", "65 x 6", 3.1, 0.180, 2, 1.12],
        ["CENTRE BRACKET", "FLAT", "65 x 6", 3.1, 0.380, 2, 2.36],
        ["SUPPORT ANGLE", "ANGLE", "50 x 50 x 6", 4.5, 0.050, 2, 0.45],
        ["GUIDE BRACKET", "FLAT", "75 x 6", 3.5, 0.150, 2, 1.05],
        ["MOUNTING ANGLE", "ANGLE", "75 x 75 x 6", 6.8, 0.240, 2, 3.26],
    ]),
    800: make_df([
        ["BASE CHANNEL", "CHANNEL", "ISMC 100 x 50", 9.2, 0.954, 1, 8.78],
        ["BRG. ANGLE", "ANGLE", "75 x 75 x 6", 6.8, 1.310, 1, 8.91],
        ["SIDE BRACKET", "FLAT", "75 x 6", 3.5, 0.190, 2, 1.33],
        ["CENTRE BRACKET", "FLAT", "75 x 6", 3.5, 0.405, 2, 2.84],
        ["SUPPORT ANGLE", "ANGLE", "50 x 50 x 6", 4.5, 0.050, 2, 0.45],
        ["GUIDE BRACKET", "FLAT", "100 x 6", 4.7, 0.160, 2, 1.50],
        ["MOUNTING ANGLE", "ANGLE", "90 x 90 x 6", 8.2, 0.240, 2, 3.94],
    ]),
    1000: make_df([
        ["BASE CHANNEL", "CHANNEL", "ISMC 125 x 65", 12.7, 1.150, 1, 14.61],
        ["BRG. ANGLE", "ANGLE", "90 x 90 x 6", 8.2, 1.565, 1, 12.83],
        ["SIDE BRACKET", "FLAT", "75 x 8", 4.7, 0.200, 2, 1.88],
        ["CENTRE BRACKET", "FLAT", "75 x 8", 4.7, 0.440, 2, 4.14],
        ["SUPPORT ANGLE", "ANGLE", "50 x 50 x 6", 4.5, 0.050, 2, 0.45],
        ["GUIDE BRACKET", "FLAT", "100 x 6", 4.7, 0.160, 2, 1.50],
        ["MOUNTING ANGLE", "ANGLE", "100 x 100 x 8", 12.1, 0.240, 2, 5.81],
    ]),
    1200: make_df([
        ["BASE CHANNEL", "CHANNEL", "ISMC 125 x 65", 12.7, 1.350, 1, 17.15],
        ["BRG. ANGLE", "ANGLE", "90 x 90 x 6", 8.2, 1.810, 1, 14.84],
        ["SIDE BRACKET", "FLAT", "75 x 8", 4.7, 0.190, 2, 1.79],
        ["CENTRE BRACKET", "FLAT", "75 x 8", 4.7, 0.425, 2, 4.00],
        ["SUPPORT ANGLE", "ANGLE", "50 x 50 x 6", 4.5, 0.050, 2, 0.45],
        ["GUIDE BRACKET", "FLAT", "130 x 8", 8.2, 0.170, 2, 2.79],
        ["MOUNTING ANGLE", "ANGLE", "100 x 100 x 8", 12.1, 0.240, 2, 5.81],
    ]),
    1400: make_df([
        ["BASE CHANNEL", "CHANNEL", "ISMC 150 x 75", 16.4, 1.550, 1, 25.42],
        ["BRG. ANGLE", "ANGLE", "100 x 100 x 8", 12.1, 2.030, 1, 24.56],
        ["SIDE BRACKET", "FLAT", "75 x 8", 4.7, 0.205, 2, 1.93],
        ["CENTRE BRACKET", "FLAT", "75 x 8", 4.7, 0.450, 2, 4.23],
        ["SUPPORT ANGLE", "ANGLE", "50 x 50 x 6", 4.5, 0.050, 2, 0.45],
        ["GUIDE BRACKET", "FLAT", "130 x 8", 8.2, 0.170, 2, 2.79],
        ["MOUNTING ANGLE", "ANGLE", "100 x 100 x 8", 12.1, 0.240, 2, 5.81],
    ]),
    1600: make_df([
        ["BASE CHANNEL", "CHANNEL", "ISMC 150 x 75", 16.4, 1.760, 1, 28.86],
        ["BRG. ANGLE", "ANGLE", "100 x 100 x 8", 12.1, 2.240, 1, 27.10],
        ["SIDE BRACKET", "FLAT", "75 x 8", 4.7, 0.205, 2, 1.93],
        ["CENTRE BRACKET", "FLAT", "75 x 8", 4.7, 0.450, 2, 4.23],
        ["SUPPORT ANGLE", "ANGLE", "50 x 50 x 6", 4.5, 0.050, 2, 0.45],
        ["GUIDE BRACKET", "FLAT", "130 x 8", 8.2, 0.170, 2, 2.79],
        ["MOUNTING ANGLE", "ANGLE", "100 x 100 x 8", 12.1, 0.240, 2, 5.81],
    ]),
    1800: make_df([
        ["BASE CHANNEL", "CHANNEL", "ISMC 150 x 75", 16.4, 1.950, 1, 31.98],
        ["BRG. ANGLE", "ANGLE", "110 x 110 x 10", 16.5, 2.445, 1, 40.34],
        ["SIDE BRACKET", "FLAT", "75 x 8", 4.7, 0.220, 2, 2.07],
        ["CENTRE BRACKET", "FLAT", "75 x 8", 4.7, 0.470, 2, 4.42],
        ["SUPPORT ANGLE", "ANGLE", "50 x 50 x 6", 4.5, 0.050, 2, 0.45],
        ["GUIDE BRACKET", "FLAT", "130 x 8", 8.2, 0.185, 2, 3.03],
        ["MOUNTING ANGLE", "ANGLE", "110 x 110 x 10", 16.5, 0.260, 2, 8.58],
    ]),
    2000: make_df([
        ["BASE CHANNEL", "CHANNEL", "ISMC 150 x 75", 16.4, 2.150, 1, 35.26],
        ["BRG. ANGLE", "ANGLE", "130 x 130 x 10", 19.7, 2.650, 1, 52.21],
        ["SIDE BRACKET", "FLAT", "75 x 8", 4.7, 0.215, 2, 2.02],
        ["CENTRE BRACKET", "FLAT", "75 x 8", 4.7, 0.460, 2, 4.32],
        ["SUPPORT ANGLE", "ANGLE", "50 x 50 x 6", 4.5, 0.050, 2, 0.45],
        ["GUIDE BRACKET", "FLAT", "130 x 8", 8.2, 0.190, 2, 3.12],
        ["MOUNTING ANGLE", "ANGLE", "110 x 110 x 10", 16.5, 0.300, 2, 9.90],
    ]),
}

# ✅ SARI tables present (you already pasted)
SARI_FAB = {
    650: make_df([
        ["BASE CHANNEL",  "ISMC",  "100 x 50",        0.972, 9.2, 1,  8.94],
        ["BRG. ANGLE",    "ANGLE", "65 x 65 x 6",     0.790, 5.8, 1,  4.58],
        ["SIDE BRACKET",  "FLAT",  "65 x 6",          0.125, 3.1, 2,  0.78],
        ["SUPPORT ANGLE", "ANGLE", "50 x 50 x 6",     0.050, 4.5, 2,  0.45],
        ["GUIDE BRACKET", "FLAT",  "75 x 6",          0.150, 3.5, 2,  1.05],
        ["MOUNTING FLAT", "FLAT",  "100 x 6",         0.330, 4.7, 2,  3.10],
    ]),
    800: make_df([
        ["BASE CHANNEL",  "ISMC",  "100 x 50",        1.122, 9.2, 1, 10.32],
        ["BRG. ANGLE",    "ANGLE", "75 x 75 x 6",     0.990, 6.8, 1,  6.73],
        ["SIDE BRACKET",  "FLAT",  "75 x 6",          0.130, 3.5, 2,  0.91],
        ["SUPPORT ANGLE", "ANGLE", "50 x 50 x 6",     0.050, 4.5, 2,  0.45],
        ["GUIDE BRACKET", "FLAT",  "100 x 6",         0.160, 4.7, 2,  1.50],
        ["MOUNTING FLAT", "FLAT",  "100 x 6",         0.340, 4.7, 2,  3.20],
    ]),
    1000: make_df([
        ["BASE CHANNEL",  "ISMC",  "125 x 65",        1.334, 12.7, 1, 16.94],
        ["BRG. ANGLE",    "ANGLE", "90 x 90 x 6",     1.194,  8.2, 1,  9.79],
        ["SIDE BRACKET",  "FLAT",  "75 x 8",          0.130,  4.7, 2,  1.22],
        ["SUPPORT ANGLE", "ANGLE", "50 x 50 x 6",     0.050,  4.5, 2,  0.45],
        ["GUIDE BRACKET", "FLAT",  "100 x 6",         0.160,  4.7, 2,  1.50],
        ["MOUNTING FLAT", "FLAT",  "130 x 8",         0.380,  8.2, 2,  6.23],
    ]),
    1200: make_df([
        ["BASE CHANNEL",  "ISMC",  "125 x 65",        1.544, 12.7, 1, 19.61],
        ["BRG. ANGLE",    "ANGLE", "90 x 90 x 6",     1.444,  8.2, 1, 11.84],
        ["SIDE BRACKET",  "FLAT",  "75 x 8",          0.130,  4.7, 2,  1.22],
        ["SUPPORT ANGLE", "ANGLE", "50 x 50 x 6",     0.050,  4.5, 2,  0.45],
        ["GUIDE BRACKET", "FLAT",  "130 x 8",         0.160,  8.2, 2,  2.62],
        ["MOUNTING FLAT", "FLAT",  "130 x 8",         0.380,  8.2, 2,  6.23],
    ]),
    1400: make_df([
        ["BASE CHANNEL",  "ISMC",  "150 x 75",        1.744, 16.4, 1, 28.60],
        ["BRG. ANGLE",    "ANGLE", "100 x 100 x 8",   1.644, 12.1, 1, 19.89],
        ["SIDE BRACKET",  "FLAT",  "75 x 8",          0.140,  4.7, 2,  1.32],
        ["SUPPORT ANGLE", "ANGLE", "50 x 50 x 6",     0.050,  4.5, 2,  0.45],
        ["GUIDE BRACKET", "FLAT",  "130 x 8",         0.170,  8.2, 2,  2.79],
        ["MOUNTING FLAT", "FLAT",  "150 x 8",         0.420,  9.4, 2,  7.90],
    ]),
    1600: make_df([
        ["BASE CHANNEL",  "ISMC",  "150 x 75",        1.954, 16.4, 1, 32.05],
        ["BRG. ANGLE",    "ANGLE", "100 x 100 x 8",   1.844, 12.1, 1, 22.31],
        ["SIDE BRACKET",  "FLAT",  "75 x 8",          0.140,  4.7, 2,  1.32],
        ["SUPPORT ANGLE", "ANGLE", "50 x 50 x 6",     0.050,  4.5, 2,  0.45],
        ["GUIDE BRACKET", "FLAT",  "130 x 8",         0.170,  8.2, 2,  2.79],
        ["MOUNTING FLAT", "FLAT",  "150 x 8",         0.420,  9.4, 2,  7.90],
    ]),
    1800: make_df([
        ["BASE CHANNEL",  "ISMC",  "150 x 75",        2.150, 16.4, 1, 35.26],
        ["BRG. ANGLE",    "ANGLE", "110 x 110 x 10",  2.044, 16.5, 1, 33.73],
        ["SIDE BRACKET",  "FLAT",  "75 x 8",          0.150,  4.7, 2,  1.41],
        ["SUPPORT ANGLE", "ANGLE", "50 x 50 x 6",     0.050,  4.5, 2,  0.45],
        ["GUIDE BRACKET", "FLAT",  "130 x 8",         0.180,  8.2, 2,  2.95],
        ["MOUNTING FLAT", "FLAT",  "150 x 8",         0.460,  9.4, 2,  8.65],
    ]),
    2000: make_df([
        ["BASE CHANNEL",  "ISMC",  "150 x 75",        2.350, 16.4, 1, 38.54],
        ["BRG. ANGLE",    "ANGLE", "130 x 130 x 10",  2.244, 19.7, 1, 44.21],
        ["SIDE BRACKET",  "FLAT",  "75 x 8",          0.165,  4.7, 2,  1.55],
        ["SUPPORT ANGLE", "ANGLE", "50 x 50 x 6",     0.050,  4.5, 2,  0.45],
        ["GUIDE BRACKET", "FLAT",  "130 x 8",         0.160,  8.2, 2,  2.62],
        ["MOUNTING FLAT", "FLAT",  "150 x 8",         0.490,  9.4, 2,  9.21],
    ]),
}

# ✅ THIS WAS YOUR BUG:
# You defined SARI_N_FAB with data above, then overwrote it to {} later.
# DO NOT overwrite it. Keep the populated dict.
SARI_N_FAB = {
    800: make_df([
        ["BASE CHANNEL", "ISMC", "100 x 50", 1.148, 9.2, 1, 10.56],
        ["BRG. ANGLE", "ANGLE", "65 x 65 x 6", 1.042, 5.8, 1, 6.04],
        ["SIDE BRACKET", "FLAT", "65 x 6", 0.152, 3.5, 2, 1.06],
        ["SUPPORT ANGLE", "ANGLE", "50 x 50 x 6", 0.050, 4.5, 2, 0.45],
        ["GUIDE BRACKET", "ANGLE", "50 x 50 x 6", 0.185, 4.5, 2, 1.67],
        ["MOUNTING FLAT", "FLAT", "110 x 6", 0.387, 5.0, 2, 3.87],
    ]),
    1000: make_df([
        ["BASE CHANNEL", "ISMC", "100 x 50", 1.348, 9.2, 1, 12.40],
        ["BRG. ANGLE", "ANGLE", "65 x 65 x 6", 1.242, 5.8, 1, 7.20],
        ["SIDE BRACKET", "FLAT", "65 x 6", 0.152, 3.5, 2, 1.06],
        ["SUPPORT ANGLE", "ANGLE", "50 x 50 x 6", 0.050, 4.5, 2, 0.45],
        ["GUIDE BRACKET", "ANGLE", "50 x 50 x 6", 0.185, 4.5, 2, 1.67],
        ["MOUNTING FLAT", "FLAT", "110 x 6", 0.387, 5.0, 2, 3.87],
    ]),
    1200: make_df([
        ["BASE CHANNEL", "ISMC", "100 x 50", 1.548, 9.2, 1, 14.24],
        ["BRG. ANGLE", "ANGLE", "65 x 65 x 6", 1.442, 5.8, 1, 8.36],
        ["SIDE BRACKET", "FLAT", "65 x 6", 0.191, 3.5, 2, 1.34],
        ["SUPPORT ANGLE", "ANGLE", "50 x 50 x 6", 0.050, 4.5, 2, 0.45],
        ["GUIDE BRACKET", "ANGLE", "50 x 50 x 6", 0.190, 4.5, 2, 1.71],
        ["MOUNTING FLAT", "FLAT", "110 x 6", 0.409, 5.0, 2, 4.09],
    ]),
}



# ================== UI ==================
st.title("COST 🚧")
st.markdown("<h6 style='color:blue;'>By SIMPLICITY</h6>", unsafe_allow_html=True)


# ================== SELECT ==================
if st.session_state.stage=="select_roller":

    main = st.selectbox("Roller Type",[
        "Select Roller",
        "Carrying Idler Without Frame",
        "Impact Idler Without Frame",
        "Carrying Idler With Frame",
        "SARI",
        "SACI"
    ])

    roller = main

    if main=="SARI":
        roller = st.radio("SARI Type",["SARI","SARI (N-6012)"],horizontal=True)

    if st.button("Proceed"):

        if roller=="Select Roller":
            st.warning("Select roller")
        else:
            st.session_state.selected_roller=roller
            st.session_state.stage="ask_constants"
            st.rerun()


# ================== CONSTANT ASK ==================
if st.session_state.stage=="ask_constants":

    st.subheader("Change Constants?")

    c1,c2=st.columns(2)

    if c1.button("YES"):
        st.session_state.stage="constants"
        st.rerun()

    if c2.button("NO"):
        st.session_state.constants=DEFAULT_CONSTANTS.copy()
        st.session_state.stage="input"
        st.rerun()


# ================== CONSTANT EDIT ==================
if st.session_state.stage=="constants":

    st.subheader("Edit Constants")

    c={}
    cols=st.columns(3)

    for i,(k,v) in enumerate(DEFAULT_CONSTANTS.items()):
        with cols[i%3]:
            c[k]=st.number_input(k,value=float(v),min_value=0.0)

    if st.button("Save"):
        st.session_state.constants=c
        st.session_state.stage="input"
        st.rerun()


# ================== INPUT (CLEAN + NO ERRORS) ==================
# ================== INPUT (FIXED) ==================
if st.session_state.stage == "input":
    st.subheader(f"Roller: {st.session_state.selected_roller}")

    # ✅ Keep these INSIDE input page so they don't show on other pages
    BEARING_OPTIONS = {
        "420201 (12 mm bore)": 12,
        "420202 (15 mm bore)": 15,
        "420203 (17 mm bore)": 17,
        "420204 (20 mm bore)": 20,
        "420205 (25 mm bore)": 25,
        "420206 (30 mm bore)": 30,
        "6203 (17 mm bore)": 17,
        "6204 (20 mm bore)": 20,
        "6205 (25 mm bore)": 25,
        "6206 (30 mm bore)": 30,
        "6304 (20 mm bore)": 20,
        "6305 (25 mm bore)": 25,
        "6306 (30 mm bore)": 30,
    }

    MARKET_SHAFT_SIZES = [12, 15, 17, 20, 25, 30, 35, 40, 45, 50]

    # --- QTY + TYPE ---
    qty_col1, qty_col2 = st.columns([1, 2])
    with qty_col1:
        qty = st.number_input("QTY", value=1, min_value=1, step=1, key="qty_input")
    with qty_col2:
        qty_type = st.radio(
            "QTY TYPE",
            ["SINGLE ROLLER", "SET (1 Frame)"],
            horizontal=True,
            key="qty_type_radio",
        )

    roller_qty = int(qty) * 3 if qty_type == "SET (1 Frame)" else int(qty)
    st.caption(
        f"Roller Qty Used = {roller_qty}  "
        f"(QTY={int(qty)} × {'3' if qty_type=='SET (1 Frame)' else '1'})"
    )

    st.markdown("---")

    # --- PIPE + FACE WIDTH ---
    c1, c2 = st.columns([1, 1])

    with c1:
        pipe_dia = st.number_input("PIPE DIA (mm)", value=89.0, min_value=0.0, step=0.1, key="pipe_dia")
        pipe_thk = st.number_input("PIPE THK (mm)", value=3.2, min_value=0.0, step=0.1, key="pipe_thk")

    with c2:
        fw_mode = st.radio("FACE WIDTH MODE", ["Manual", "Get Face Width"], horizontal=True, key="fw_mode")

        if fw_mode == "Manual":
            face_width = st.number_input(
                "FACE WIDTH (mm)",
                value=190.0,
                min_value=0.0,
                step=1.0,
                key="face_width_manual",
            )
        else:
            bw_input = st.number_input(
                "Enter Belt Width (mm)",
                value=650,
                min_value=0,
                step=50,
                key="bw_input_fw",
            )

            if bw_input < 800:
                add_val = 100
            elif bw_input == 800:
                add_val = 150
            elif bw_input == 1000:
                add_val = 200
            elif bw_input >= 1500:
                add_val = 250
            else:
                add_val = 150

            face_width = (bw_input + add_val) / 3
            st.success(f"Calculated Face Width = {round(face_width, 2)} mm")

    # ✅ Save face width safely for any later reference
    st.session_state["face_width"] = float(face_width)

    st.markdown("---")

    # --- SHAFT (bearing + recommended dia + recommended length) ---
    sh1, sh2 = st.columns([1, 1])

    with sh1:
        bearing_choice = st.selectbox(
            "BEARING STANDARD (Make: SKF/FAG/TATA/NBC etc.)",
            list(BEARING_OPTIONS.keys()),
            key="bearing_choice",
        )

        bore = int(BEARING_OPTIONS[bearing_choice])
        target = bore + 5
        rec_shaft_dia = next((s for s in MARKET_SHAFT_SIZES if s >= target), target)

        st.caption(f"Inner Bore = {bore} mm → Recommended Shaft Dia = {rec_shaft_dia} mm")

        shaft_dia = st.number_input(
            "SHAFT DIA (mm)",
            value=float(rec_shaft_dia),
            min_value=0.0,
            step=1.0,
            key="shaft_dia",
        )

    with sh2:
        fw = float(st.session_state.get("face_width", 190.0))
        rec_shaft_len = fw + 60.0

        st.caption(f"Recommended Shaft Length = Face Width + 60 = {round(rec_shaft_len, 2)} mm")

        shaft_len = st.number_input(
            "SHAFT LENGTH (mm)",
            value=float(rec_shaft_len),
            min_value=0.0,
            step=1.0,
            key="shaft_len",
        )

    st.markdown("---")

    # --- WEIGHT CALC (✅ must be inside input block so variables exist) ---
    pipe_wt = (3.14 * pipe_dia * face_width * pipe_thk * 7.85) / 1e6
    shaft_wt = (3.14 / 4) * (shaft_dia / 10) ** 2 * (shaft_len / 10) * 7.85 / 1000
    total_wt = pipe_wt + shaft_wt
    st.session_state.last_roller_weight = float(total_wt)

    # --- COSTING ---
    c = st.session_state.constants
    housing_cost = pipe_dia / 2

    unit_cp = (
        total_wt * c["STEEL_COST"]
        + housing_cost
        + c["BEARING_COST_PAIR"]
        + c["SEAL_COST"]
        + c["WELDING_COST"]
        + c.get("GUIDE_ROLLER", 0.0)
        + c.get("PIVOT_BEARING", 0.0)
        + c.get("LOCKING_RING", 0.0)
    )

    unit_price = unit_cp * c["MARKUP"]
    total_price = unit_price * roller_qty

    st.info(
        f"Roller Weight = {round(total_wt,3)} kg | "
        f"Unit Price = {round(unit_price,2)} | "
        f"Total Price = {round(total_price,2)}"
    )

    # --- SAVE BUTTON ---
    if st.button("Calculate Roller Cost", key="btn_calc_roller_cost"):
        st.session_state.costings.append(
            {
                "ROLLER": st.session_state.selected_roller,
                "WT": round(total_wt, 3),
                "QTY": int(qty),
                "QTY TYPE": qty_type,
                "ROLLER QTY": int(roller_qty),
                "UNIT_CP": round(unit_cp, 2),
                "UNIT_PRICE": round(unit_price, 2),
                "TOTAL_PRICE": round(total_price, 2),
            }
        )
        st.session_state.stage = "compiled"
        st.rerun()
          # ================== COMPILED ==================
# ================== COMPILED (ONLY ONE BLOCK) ==================
if st.session_state.stage == "compiled":
    st.subheader("Roller Costing")

    if not st.session_state.costings:
        st.warning("No roller costing saved yet. Go back and calculate.")
    else:
        st.dataframe(pd.DataFrame(st.session_state.costings), use_container_width=True)

    r = st.session_state.selected_roller

    # frame not applicable warning
    if r in ["Carrying Idler Without Frame", "Impact Idler Without Frame"]:
        st.warning("Frame Not Applicable for this roller type.")

    c1, c2, c3 = st.columns(3)

    # ✅ Back
    if c1.button("Back", key="compiled_back_btn"):
        st.session_state.stage = "input"
        st.rerun()

    # ✅ Frame Cost (only if applicable)
    if c2.button("Frame Cost", key="compiled_frame_btn"):
        if r in ["Carrying Idler Without Frame", "Impact Idler Without Frame"]:
            st.error("No Frame for this roller.")
        else:
            st.session_state.stage = "frame_input"
            st.rerun()

    # ✅ New Roller (unique key)
    if c3.button("New Roller", key="compiled_new_btn"):
        st.session_state.stage = "select_roller"
        st.rerun()

# ================== FRAME INPUT (FULL FIXED BLOCK) ==================
# ================== ROLLER WT → FRAME BW MAP ==================
ROLLER_WT_TO_BW = [
    (0, 15, 650),
    (15, 22, 800),
    (22, 30, 1000),
    (30, 38, 1200),
    (38, 48, 1400),
    (48, 60, 1600),
    (60, 75, 1800),
    (75, 10**9, 2000),
]

def get_frame_bw_from_roller_wt(roller_wt: float) -> int:
    """Map roller weight (kg) to a belt width (mm)."""
    for low, high, bw in ROLLER_WT_TO_BW:
        if low <= roller_wt < high:
            return bw
    return 1000
if st.session_state.stage == "frame_input":

    st.subheader("Frame Costing")

    roller     = st.session_state.selected_roller
    roller_wt  = st.session_state.last_roller_weight
    c          = st.session_state.constants

    # --- Get last roller row safely ---
    if not st.session_state.costings:
        st.error("No roller costing found. Go back and calculate roller first.")
        st.stop()

    last_roller = st.session_state.costings[-1]

    # --- Get quantity & qty type safely ---
    set_qty  = int(last_roller.get("QTY", 1))
    qty_type = str(last_roller.get("QTY TYPE", "")).strip()

    # ✅ FIX: Accept anything starting with SET
    if not qty_type.upper().startswith("SET"):
        st.error("Frame costing only applies when QTY TYPE is SET.")
        st.stop()

    # --- Auto belt width selection ---
    bw = get_frame_bw_from_roller_wt(roller_wt)

    st.info(f"Auto Selected Frame BW = {bw} mm (from Roller WT = {round(roller_wt,2)} kg)")

    # --- Select correct frame weight + fab table ---
    if roller == "Carrying Idler With Frame":
        frame_wt = safe_get(CARRYING_FRAME_WT, bw, "Carrying Frame Weight")
        fab      = safe_get(CARRYING_FAB, bw, "Carrying Fabrication Table")

    elif roller == "SARI":
        frame_wt = safe_get(SARI_FRAME_WT, bw, "SARI Frame Weight")
        fab      = safe_get(SARI_FAB, bw, "SARI Fabrication Table")

    elif roller == "SARI (N-6012)":
        if bw not in SARI_N_FRAME_WT:
            bw = min(SARI_N_FRAME_WT.keys(), key=lambda k: abs(k-bw))
        frame_wt = safe_get(SARI_N_FRAME_WT, bw, "SARI N Frame Weight")
        fab      = safe_get(SARI_N_FAB, bw, "SARI N Fabrication Table")

    elif roller == "SACI":
        frame_wt = safe_get(SACI_FRAME_WT, bw, "SACI Frame Weight")
        fab      = safe_get(SACI_FAB, bw, "SACI Fabrication Table")

    else:
        st.error("Frame not defined for this roller.")
        st.stop()

    # --- Show reference tables ---
    st.subheader("Frame Weight Reference")
    st.success(f"Selected Frame Weight = {frame_wt} kg")

    st.subheader("Fabrication Table (Editable)")
    edited = st.data_editor(fab, use_container_width=True)

    # --- Calculate frame weight from fabrication ---
    if "TOTAL WT" in edited.columns and not edited.empty:
        total_frame_wt = edited["TOTAL WT"].sum()
    else:
        total_frame_wt = frame_wt

    # --- Frame costing ---
    frame_unit_cost  = total_frame_wt*c["STEEL_COST"] + c["FRAME_RATE"] + c["WELDING_COST"]
    frame_unit_price = frame_unit_cost * c["MARKUP"]

    # ✅ IMPORTANT: Frame total price = SET QTY × UNIT PRICE
    frame_total_price = frame_unit_price * set_qty

    st.metric("Frame Unit Price", round(frame_unit_price,2))
    st.metric("Frame Total Price", round(frame_total_price,2))

    if st.button("Add Frame Cost"):

        st.session_state.frame_costings.append({
            "ROLLER": roller,
            "BELT WIDTH": bw,
            "FRAME UNIT PRICE": round(frame_unit_price,2),
            "FRAME TOTAL PRICE": round(frame_total_price,2),
            "FRAME QTY (SET)": set_qty
        })

        st.session_state.stage = "frame_compiled"
        st.rerun()

    if st.button("Back"):
        st.session_state.stage = "compiled"
        st.rerun()

      

# ================== FRAME COMPILED (FULL FIXED BLOCK) ==================
if st.session_state.stage == "frame_compiled":
    st.subheader("Frame Costing Table")
    st.dataframe(pd.DataFrame(st.session_state.frame_costings), use_container_width=True)

    if st.session_state.costings and st.session_state.frame_costings:
        last_roller = st.session_state.costings[-1]
        last_frame  = st.session_state.frame_costings[-1]

        roller_total = float(last_roller.get("TOTAL_PRICE", 0))
        frame_total  = float(last_frame.get("FRAME TOTAL PRICE", 0))

        st.markdown("### Total Cost (Roller + Frame)")
        total_df = pd.DataFrame([{
            "ROLLER TOTAL PRICE": round(roller_total, 2),
            "FRAME TOTAL PRICE": round(frame_total, 2),
            "TOTAL (ROLLER + FRAME)": round(roller_total + frame_total, 2),
        }])
        st.dataframe(total_df, use_container_width=True)

    st.markdown("---")
    c1, c2 = st.columns(2)

    if c1.button("Back to Roller Costing", key="btn_back_to_roller_costing_frame_compiled"):
        st.session_state.stage = "compiled"
        st.rerun()

    if c2.button("Calculate New Roller", key="btn_new_roller_from_frame_compiled"):
        st.session_state.stage = "select_roller"
        st.rerun()
# ================== DOWNLOAD ==================
if st.session_state.costings:

    buf=BytesIO()

    with pd.ExcelWriter(buf,engine="xlsxwriter") as w:
        pd.DataFrame(st.session_state.costings).to_excel(w,index=False)

    st.download_button("Download Roller",buf.getvalue(),"roller.xlsx")


if st.session_state.frame_costings:

    buf=BytesIO()

    with pd.ExcelWriter(buf,engine="xlsxwriter") as w:
        pd.DataFrame(st.session_state.frame_costings).to_excel(w,index=False)

    st.download_button("Download Frame",buf.getvalue(),"frame.xlsx")
