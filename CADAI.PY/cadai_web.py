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

# ================== CONSTANTS ==================
DEFAULT_CONSTANTS = {
    "STEEL_COST": 70.0,
    "BEARING_COST_PAIR": 100.0,
    "SEAL_COST": 30.0,
    "WELDING_COST": 80.0,
    "MARKUP": 1.25,
    "FRAME_RATE": 100.0,
    # keep keys available even if you don't use now
    "GUIDE_ROLLER": 0.0,
    "PIVOT_BEARING": 0.0,
}

# ================== HELPERS ==================
def make_df(rows):
    if rows is None or len(rows) == 0:
        # return empty df with base columns so editor & sums don't crash
        return pd.DataFrame(columns=["DESCRIPTION","SECTION","SIZE","WT/M","LENGTH (M)","QTY","TOTAL WT"])

    max_len = max(len(r) for r in rows)

    base_cols = ["DESCRIPTION","SECTION","SIZE","WT/M","LENGTH (M)","QTY","TOTAL WT"]

    if max_len > len(base_cols):
        extra = [f"EXTRA_{i}" for i in range(max_len - len(base_cols))]
        cols = base_cols + extra
    else:
        cols = base_cols[:max_len]

    fixed_rows = []
    for r in rows:
        if len(r) < max_len:
            r = r + [None] * (max_len - len(r))
        fixed_rows.append(r)

    return pd.DataFrame(fixed_rows, columns=cols)

def safe_get(table, key, label):
    if key not in table:
        st.error(f"{label} not available for belt width {key} mm")
        st.stop()
    return table[key]

# ================== FRAME WEIGHT TABLES ==================
CARRYING_FRAME_WT = {650:12.7,800:16.8,1000:23.1,1200:26.2,1400:35.0,1600:38.4,1800:52.4,2000:64.7}
SARI_FRAME_WT     = {650:14.2,800:18.1,1000:24.5,1200:28.9,1400:37.4,1600:41.8,1800:56.2,2000:68.9}
SARI_N_FRAME_WT   = {800:19.3,1000:26.1,1200:30.2}
SACI_FRAME_WT     = {650:13.5,800:17.2,1000:22.9,1200:27.4,1400:36.2,1600:40.5,1800:54.3,2000:66.1}

# ================== ROLLER WT → FRAME BW MAP ==================
ROLLER_WT_TO_BW = [
    (0, 15, 650),
    (15, 22, 800),
    (22, 30, 1000),
    (30, 38, 1200),
    (38, 48, 1400),
    (48, 60, 1600),
    (60, 75, 1800),
    (75, 1000, 2000),
]

def get_frame_bw_from_roller_wt(roller_wt):
    for low, high, bw in ROLLER_WT_TO_BW:
        if low <= roller_wt < high:
            return bw
    return 1000

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
st.title("COSTY 🚧")

st.markdown(
    "<h6 style='color:blue;'>By SIMPLICITY</h6>",
    unsafe_allow_html=True
)
# ---------------- SELECT ----------------
if st.session_state.stage=="select_roller":

    main_roller = st.selectbox("Roller Type",[
        "Select Roller",
        "Carrying Idler Without Frame",
        "Impact Idler Without Frame",
        "Carrying Idler With Frame",
        "SARI",
        "SACI",
        "Belt Conveyor"
    ])

    roller = main_roller

    if main_roller == "SARI":
        sari_type = st.radio("Select SARI Type",["SARI","SARI (N-6012)"],horizontal=True)
        roller = sari_type

    if st.button("Proceed"):
        if roller=="Select Roller":
            st.warning("Select roller")
        elif roller=="Belt Conveyor":
            st.error("Module under construction")
        else:
            st.session_state.selected_roller = roller
            st.session_state.stage="ask_constants"
            st.rerun()

# ---------------- CONSTANTS ASK ----------------
if st.session_state.stage=="ask_constants":
    st.subheader("Change Fixed Constants?")
    c1,c2=st.columns(2)
    if c1.button("YES"):
        st.session_state.stage="constants"; st.rerun()
    if c2.button("NO"):
        st.session_state.constants=DEFAULT_CONSTANTS.copy()
        st.session_state.stage="input"; st.rerun()

# ---------------- CONSTANTS ----------------
if st.session_state.stage=="constants":
    st.subheader("Edit Constants")
    c={}
    cols=st.columns(3)
    for i,(k,v) in enumerate(DEFAULT_CONSTANTS.items()):
        with cols[i%3]:
            c[k]=st.number_input(k,value=float(v), min_value=0.0)
    if st.button("Save"):
        st.session_state.constants=c
        st.session_state.stage="input"
        st.rerun()

# ---------------- INPUT ----------------
if st.session_state.stage=="input":
    st.subheader(f"Roller: {st.session_state.selected_roller}")

    pipe_dia=st.number_input("PIPE DIAMETER", value=89.0, min_value=0.0)
    face_width=st.number_input("FACE WIDTH", value=190.0, min_value=0.0)
    shaft_dia=st.number_input("SHAFT DIA", value=25.0, min_value=0.0)
    shaft_len=st.number_input("SHAFT LENGTH", value=220.0, min_value=0.0)
    pipe_thk=st.number_input("PIPE THK", value=3.2, min_value=0.0)
    qty=st.number_input("QTY", value=1, min_value=1, step=1)

    pipe_wt=(3.14*pipe_dia*face_width*pipe_thk*7.85)/1000000
    shaft_wt=(3.14/4)*(shaft_dia/10)**2*(shaft_len/10)*7.85/1000
    total_wt=pipe_wt+shaft_wt

    st.session_state.last_roller_weight = total_wt

    c=st.session_state.constants
    housing_cost=pipe_dia/2

    total_cost=total_wt*c["STEEL_COST"]+housing_cost+c["BEARING_COST_PAIR"]+c["SEAL_COST"]+c["WELDING_COST"]+c["GUIDE_ROLLER"]+c["PIVOT_BEARING"]
    unit_price=total_cost*c["MARKUP"]
    total_price=unit_price*qty

    if st.button("Calculate Roller Cost"):
        st.session_state.costings.append({
            "ROLLER":st.session_state.selected_roller,
            "WT":round(total_wt,3),
            "QTY":qty,
            "UNIT_CP":round(total_cost,2),
            "UNIT_PRICE":round(unit_price,2),
            "TOTAL_PRICE":round(total_price,2)
        })
        st.session_state.stage="compiled"
        st.rerun()

# ---------------- COMPILED ----------------
if st.session_state.stage=="compiled":
    st.subheader("Roller Costing")
    st.dataframe(pd.DataFrame(st.session_state.costings),use_container_width=True)

    roller = st.session_state.selected_roller

    if roller in ["Carrying Idler Without Frame","Impact Idler Without Frame"]:
        st.warning("Frame cost not applicable for this roller type")

    c1,c2=st.columns(2)
    if c1.button("Calculate Frame Cost"):
        if roller in ["Carrying Idler Without Frame","Impact Idler Without Frame"]:
            st.error("Frame not applicable")
        else:
            st.session_state.stage="frame_input"; st.rerun()
    if c2.button("Add Another Roller"):
        st.session_state.stage="select_roller"; st.rerun()

# ---------------- FRAME INPUT ----------------
if st.session_state.stage=="frame_input":
    st.subheader("Frame Costing")

    roller=st.session_state.selected_roller
    roller_wt=st.session_state.last_roller_weight
    c=st.session_state.constants

    bw = get_frame_bw_from_roller_wt(roller_wt)

    # ✅ Critical fix for SARI (N-6012): only 800/1000/1200 exist
    if roller == "SARI (N-6012)" and bw not in SARI_N_FRAME_WT:
        bw = min(SARI_N_FRAME_WT.keys(), key=lambda k: abs(k - bw))

    st.info(f"Auto Selected Frame BW = {bw} mm (from Roller WT = {round(roller_wt,2)} kg)")

    # ✅ Show respective frame weight table (not WT→BW map)
    st.subheader("Frame Weight Reference Table")
    if roller=="Carrying Idler With Frame":
        st.table(pd.DataFrame(list(CARRYING_FRAME_WT.items()), columns=["Belt Width (mm)", "Frame Weight (kg)"]))
    elif roller=="SARI":
        st.table(pd.DataFrame(list(SARI_FRAME_WT.items()), columns=["Belt Width (mm)", "Frame Weight (kg)"]))
    elif roller=="SARI (N-6012)":
        st.table(pd.DataFrame(list(SARI_N_FRAME_WT.items()), columns=["Belt Width (mm)", "Frame Weight (kg)"]))
    elif roller=="SACI":
        st.table(pd.DataFrame(list(SACI_FRAME_WT.items()), columns=["Belt Width (mm)", "Frame Weight (kg)"]))

    if roller=="Carrying Idler With Frame":
        frame_wt = safe_get(CARRYING_FRAME_WT, bw, "Carrying Frame Weight")
        fab      = safe_get(CARRYING_FAB, bw, "Carrying Fabrication Table")
    elif roller=="SARI":
        frame_wt = safe_get(SARI_FRAME_WT, bw, "SARI Frame Weight")
        fab      = safe_get(SARI_FAB, bw, "SARI Fabrication Table")
    elif roller=="SARI (N-6012)":
        frame_wt = safe_get(SARI_N_FRAME_WT, bw, "SARI N-6012 Frame Weight")
        fab      = safe_get(SARI_N_FAB, bw, "SARI N-6012 Fabrication Table")
    elif roller=="SACI":
        frame_wt = safe_get(SACI_FRAME_WT, bw, "SACI Frame Weight")
        fab      = safe_get(SACI_FAB, bw, "SACI Fabrication Table")
    else:
        st.stop()

    st.success(f"Selected Frame Weight = {frame_wt} kg")

    st.subheader("Fabrication Table (Editable)")
    edited=st.data_editor(fab,use_container_width=True)

    total_frame_wt = edited["TOTAL WT"].sum() if ("TOTAL WT" in edited.columns and not edited.empty) else frame_wt

    frame_cp=total_frame_wt*c["STEEL_COST"] + c["FRAME_RATE"] + c["WELDING_COST"]
    frame_price=frame_cp*c["MARKUP"]

    st.metric("Frame Weight Used",round(total_frame_wt,2))
    st.metric("Unit Frame Cost",round(frame_cp,2))
    st.metric("Unit Frame Price",round(frame_price,2))

    if st.button("Add Frame Cost"):
        st.session_state.frame_costings.append({
            "ROLLER":roller,
            "AUTO BW":bw,
            "FRAME WT":round(total_frame_wt,2),
            "UNIT_CP":round(frame_cp,2),
            "UNIT_PRICE":round(frame_price,2)
        })
        st.session_state.stage="frame_compiled"; st.rerun()

    if st.button("Back"):
        st.session_state.stage="compiled"; st.rerun()

# ---------------- FRAME COMPILED ----------------
# ---------------- FRAME COMPILED ----------------
if st.session_state.stage=="frame_compiled":
    st.subheader("Frame Costing Table")
    st.dataframe(pd.DataFrame(st.session_state.frame_costings), use_container_width=True)

    # ✅ 1 Set Cost (Roller + Frame)
    if st.session_state.costings and st.session_state.frame_costings:
        last_roller = st.session_state.costings[-1]
        last_frame  = st.session_state.frame_costings[-1]

        # Roller: use TOTAL_PRICE (already qty*unit price)
        roller_total = float(last_roller.get("TOTAL_PRICE", 0))

        # Frame: you said "frame total price = unit_price"
        frame_total = float(last_frame.get("UNIT_PRICE", 0))

        one_set_total = roller_total + frame_total

        st.markdown("### 1 Set Cost (Roller + Frame)")
        one_set_df = pd.DataFrame([{
            "ROLLER TOTAL PRICE": round(roller_total, 2),
            "FRAME UNIT PRICE": round(frame_total, 2),
            "1 SET TOTAL (ROLLER + FRAME)": round(one_set_total, 2)
        }])
        st.dataframe(one_set_df, use_container_width=True)

    st.markdown("---")
    c1, c2 = st.columns(2)

    # ✅ Add UNIQUE keys to avoid Streamlit duplicate button id error
    if c1.button("Back to Roller Costing", key="btn_back_to_roller_costing_frame_compiled"):
        st.session_state.stage="compiled"
        st.rerun()

    if c2.button("Calculate New Roller", key="btn_new_roller_from_frame_compiled"):
        st.session_state.stage="select_roller"
        st.rerun()

# ---------------- DOWNLOAD ----------------
if st.session_state.costings:
    buffer=BytesIO()
    with pd.ExcelWriter(buffer,engine="openpyxl") as writer:
        pd.DataFrame(st.session_state.costings).to_excel(writer,index=False,sheet_name="ROLLER")
    st.download_button("Download Roller Excel",buffer.getvalue(),"roller_costing.xlsx")

if st.session_state.frame_costings:
    buffer=BytesIO()
    with pd.ExcelWriter(buffer,engine="openpyxl") as writer:
        pd.DataFrame(st.session_state.frame_costings).to_excel(writer,index=False,sheet_name="FRAME")
    st.download_button("Download Frame Excel",buffer.getvalue(),"frame_costing.xlsx")
