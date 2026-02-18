# cadai_web.py
# FULL FIXED VERSION — Roller Selection + SARI + Carrying Idler With Frame + Frame Compiled

import streamlit as st
import pandas as pd
from io import BytesIO

# ---------------- SESSION INIT ----------------
if "stage" not in st.session_state:
    st.session_state.stage = "select_roller"

if "costings" not in st.session_state:
    st.session_state.costings = []

if "frame_costings" not in st.session_state:
    st.session_state.frame_costings = []

if "constants" not in st.session_state:
    st.session_state.constants = {}

if "selected_roller" not in st.session_state:
    st.session_state.selected_roller = None

# ---------------- CONSTANTS ----------------
DEFAULT_CONSTANTS = {
    "STEEL_COST": 70,
    "BEARING_COST_PAIR": 100,
    "SEAL_COST": 30,
    "WELDING_COST": 80,
    "MARKUP": 1.25,
    "FRAME_RATE": 100,
    "LOCKING_RING": 0
}

# ---------------- FRAME TABLE ----------------
REFERENCE_FRAME_WEIGHT_TABLE = pd.DataFrame({
    "BELT WIDTH (MM)": [650, 800, 1000, 1200, 1400, 1600, 1800, 2000],
    "TOTAL FRAME WT": [12.70, 16.76, 20.12, 26.21, 35.05, 38.44, 52.39, 64.74]
})

FRAME_TABLE = {
    650: 12.7,
    800: 16.8,
    1000: 23.1,
    1200: 26.2,
    1400: 35.0,
    1600: 38.4,
    1800: 52.4,
    2000: 64.7
}

def nearest_frame(weight):
    return min(FRAME_TABLE.items(), key=lambda x: abs(x[1] - weight))

# ---------------- UI ----------------
st.title("COST AI")

# ---------------- ROLLER SELECT ----------------
if st.session_state.stage == "select_roller":
    st.subheader("Select Roller Type")
    roller = st.selectbox(
        "Roller Type",
        [
            "Select Roller",
            "Carrying Idler Without Frame",
            "Impact Idler Without Frame",
            "Carrying Idler With Frame",
            "SARI",
            "SACI"
        ]
    )

    if roller == "SACI":
        st.warning("🚧 Under Construction — Coming Soon")

    if st.button("Proceed"):
        if roller == "Select Roller":
            st.warning("Please select a roller type")
        elif roller == "SACI":
            st.error("Module under construction")
        else:
            st.session_state.selected_roller = roller
            st.session_state.stage = "ask_constants"
            st.rerun()

# ---------------- CONSTANT CHOICE ----------------
if st.session_state.stage == "ask_constants":
    st.subheader("Change Fixed Constants?")
    col1, col2 = st.columns(2)

    if col1.button("YES"):
        st.session_state.stage = "constants"
        st.rerun()
    if col2.button("NO"):
        st.session_state.constants = DEFAULT_CONSTANTS.copy()
        st.session_state.stage = "input"
        st.rerun()

# ---------------- CONSTANTS EDIT ----------------
if st.session_state.stage == "constants":
    st.subheader("Edit Fixed Constants")
    c = {}
    cols = st.columns(3)
    i = 0
    for k,v in DEFAULT_CONSTANTS.items():
        with cols[i%3]:
            c[k] = st.number_input(k, value=float(v))
        i += 1
    if st.button("Save Constants"):
        st.session_state.constants = c
        st.session_state.stage = "input"
        st.rerun()

# ---------------- INPUT ----------------
if st.session_state.stage == "input":
    st.subheader(st.session_state.selected_roller)

    pipe_dia = st.number_input("PIPE DIAMETER", value=89.0)
    face_width = st.number_input("FACE WIDTH", value=190.0)
    shaft_dia = st.number_input("SHAFT DIAMETER", value=25.0)
    shaft_len = st.number_input("SHAFT LENGTH", value=220.0)
    pipe_thk = st.number_input("PIPE THICKNESS", value=3.2)
    qty = st.number_input("QTY", value=1, step=1)

    if int(shaft_dia) % 2 != 0:
        shaft_dia += 3

    # ---- WEIGHTS ----
    pipe_wt = (3.14*pipe_dia*face_width*pipe_thk*7.85)/1000000
    shaft_wt = (3.14/4)*(shaft_dia/10)*(shaft_dia/10)*(shaft_len/10)*7.85/1000
    total_wt = pipe_wt + shaft_wt

    c = st.session_state.constants
    housing_cost = pipe_dia / 2
    roller_type = st.session_state.selected_roller

    # ------------------ SARI ------------------
    if roller_type == "SARI":
        belt_width = 1000
        st.markdown(f"**BELT WIDTH = {belt_width} mm (Fixed for SARI)**")
        steel_cost = 70
        bearing_cost = 100
        seal_cost = 30
        welding_cost = 80
        total_cost = (total_wt*steel_cost) + housing_cost + steel_cost + bearing_cost + seal_cost + welding_cost
        unit_price = total_cost * 1.25
        total_price = unit_price * qty
        if st.button("Calculate Roller Cost"):
            st.session_state.last_roller_weight = total_wt
            st.session_state.costings.append({
                "ROLLER": "SARI",
                "WT": round(total_wt,3),
                "QTY": qty,
                "UNIT_CP": round(total_cost,2),
                "UNIT_PRICE": round(unit_price,2),
                "TOTAL_PRICE": round(total_price,2)
            })
            st.session_state.stage = "compiled"
            st.rerun()

    # ------------------ Other Rollers ------------------
    else:
        if roller_type == "Carrying Idler Without Frame":
            total_cost = (total_wt*c["STEEL_COST"])+housing_cost+c["BEARING_COST_PAIR"]+c["SEAL_COST"]+c["WELDING_COST"]
        elif roller_type == "Impact Idler Without Frame":
            rubber_ring_qty = face_width/35
            rubber_ring_cost = rubber_ring_qty*50
            total_cost = (total_wt*c["STEEL_COST"])+housing_cost+rubber_ring_cost+c["BEARING_COST_PAIR"]+c["SEAL_COST"]+c["LOCKING_RING"]+c["WELDING_COST"]
        elif roller_type == "Carrying Idler With Frame":
            total_cost = (total_wt*c["STEEL_COST"])+housing_cost+c["LOCKING_RING"]+c["BEARING_COST_PAIR"]+c["SEAL_COST"]+c["WELDING_COST"]
        unit_price = total_cost*c["MARKUP"]
        total_price = unit_price*qty
        if st.button("Calculate Roller Cost"):
            st.session_state.last_roller_weight = total_wt
            st.session_state.costings.append({
                "ROLLER": roller_type,
                "WT": round(total_wt,3),
                "QTY": qty,
                "UNIT_CP": round(total_cost,2),
                "UNIT_PRICE": round(unit_price,2),
                "TOTAL_PRICE": round(total_price,2)
            })
            st.session_state.stage = "compiled"
            st.rerun()

# ---------------- COMPILED ROLLER ----------------
if st.session_state.stage == "compiled":
    st.subheader("Roller Costing")
    df = pd.DataFrame(st.session_state.costings)
    st.dataframe(df, use_container_width=True)

    col1, col2 = st.columns(2)

    # ---- FRAME OPTION ----
    if st.session_state.selected_roller == "Carrying Idler With Frame":
        if col1.button("Calculate Frame Cost"):
            st.session_state.stage = "frame_input"
            st.rerun()
    elif st.session_state.selected_roller == "SARI":
        if col1.button("Calculate Frame Cost"):
            st.session_state.stage = "frame_input_sari"
            st.rerun()
    else:
        col1.info("Frame costing not applicable for this roller")

    if col2.button("Add Another Roller"):
        st.session_state.stage = "select_roller"
        st.rerun()

# ---------------- FRAME INPUT (Carrying Idler With Frame) ----------------
if st.session_state.stage == "frame_input":
    st.subheader("Frame Auto Selection & Calculation (Carrying Idler With Frame)")

    st.markdown("### Reference Frame Weight Table")
    st.dataframe(REFERENCE_FRAME_WEIGHT_TABLE, use_container_width=True)

    roller_wt = st.session_state.last_roller_weight
    bw, _ = nearest_frame(roller_wt)
    st.success(f"AUTO SELECTED BELT WIDTH = {bw} mm (Based on Roller WT = {round(roller_wt,2)} kg)")

    def make_df(rows):
        return pd.DataFrame(rows, columns=["DESCRIPTION","SECTION","SIZE","LENGTH (M)","WT/M","QTY","TOTAL WT"])

    FRAME_STRUCTURES = {
        650: make_df([
            ["BASE ANGLE","ANGLE","65 x 65 x 6",5.8,0.984,1,5.71],
            ["SIDE BRACKET","FLAT","65 x 6",3.1,0.345,2,2.14],
            ["CENTRE BRACKET","FLAT","65 x 6",3.1,0.365,2,2.26],
            ["MID FLAT","FLAT","50 x 6",2.4,0.300,2,1.44],
            ["BASE FLAT","FLAT","50 x 6",2.4,0.240,2,1.15],
        ]),
        800: make_df([
            ["BASE ANGLE","ANGLE","75 x 75 x 6",6.8,1.134,1,7.71],
            ["SIDE BRACKET","FLAT","75 x 6",3.5,0.385,2,2.70],
            ["CENTRE BRACKET","FLAT","75 x 6",3.5,0.400,2,2.80],
            ["MID FLAT","FLAT","50 x 6",2.4,0.500,2,2.40],
            ["BASE FLAT","FLAT","50 x 6",2.4,0.240,2,1.15],
        ]),
        1000: make_df([
            ["BASE ANGLE","ANGLE","90 x 90 x 6",6.0,1.350,1,8.10],
            ["SIDE BRACKET","FLAT","75 x 8",4.7,0.425,2,4.00],
            ["CENTRE BRACKET","FLAT","75 x 8",4.7,0.415,2,3.90],
            ["MID FLAT","FLAT","50 x 6",2.4,0.550,2,2.64],
            ["BASE FLAT","FLAT","65 x 6",3.1,0.240,2,1.49],
        ])
    }

    df = FRAME_STRUCTURES[bw]
    st.markdown("### Frame Fabrication Table (Editable)")
    edited_df = st.data_editor(df, use_container_width=True)
    TOTAL_FRAME_WEIGHT = edited_df["TOTAL WT"].sum()
    st.success(f"TOTAL FRAME WEIGHT = {round(TOTAL_FRAME_WEIGHT,2)} kg")

    QTY = st.number_input("Frame QTY", value=1, step=1)
    RATE = st.session_state.constants["FRAME_RATE"]
    MARKUP = st.session_state.constants["MARKUP"]
    UNIT_CP = TOTAL_FRAME_WEIGHT * RATE
    TOTAL_CP = UNIT_CP * QTY
    UNIT_PRICE = UNIT_CP * MARKUP
    TOTAL_PRICE = UNIT_PRICE * QTY

    if st.button("Add Frame Cost"):
        st.session_state.frame_costings.append({
            "DESCRIPTION": f"{bw} MM CARRYING FRAME",
            "FRAME_WT": round(TOTAL_FRAME_WEIGHT,2),
            "RATE": RATE,
            "UNIT_CP": round(UNIT_CP,2),
            "QTY": QTY,
            "TOTAL_CP": round(TOTAL_CP,2),
            "MARKUP": MARKUP,
            "UNIT_PRICE": round(UNIT_PRICE,2),
            "TOTAL_PRICE": round(TOTAL_PRICE,2)
        })
        st.session_state.stage = "frame_compiled"
        st.rerun()

# ---------------- FRAME INPUT FOR SARI ----------------
if st.session_state.stage == "frame_input_sari":
    st.subheader("SARI Frame Auto Selection & Calculation")
    SARI_FRAME_WT_TABLE = {650:18.9,800:23.1,1000:36.1,1200:42.0,1400:60.9,1600:66.8,1800:90.9,2000:96.6}

    roller_wt = st.session_state.last_roller_weight
    nearest_bw = min(SARI_FRAME_WT_TABLE.keys(), key=lambda x: abs(SARI_FRAME_WT_TABLE[x]-roller_wt))
    st.success(f"Selected Belt Width = {nearest_bw} mm (Based on Roller WT = {round(roller_wt,2)} kg)")

    def make_df(rows):
        return pd.DataFrame(rows, columns=["DESCRIPTION","SECTION","SIZE","WT/M","LENGTH (M)","QTY","TOTAL WT"])

    SARI_FRAME_STRUCTURES = {
        650: make_df([
            ["BASE CHANNEL","ISMC","100 x 50",0.972,9.2,1,8.94],
            ["BRG. ANGLE","ANGLE","65 x 65 x 6",0.790,5.8,1,4.58],
            ["SIDE BRACKET","FLAT","65 x 6",0.125,3.1,2,0.78],
            ["SUPPORT ANGLE","ANGLE","50 x 50 x 6",0.050,4.5,2,0.45],
            ["GUIDE BRACKET","FLAT","75 x 6",0.150,3.5,2,1.05],
            ["MOUNTING FLAT","FLAT","100 x 6",0.330,4.7,2,3.10],
        ]),
        800: make_df([
            ["BASE CHANNEL","ISMC","100 x 50",1.122,9.2,1,10.32],
            ["BRG. ANGLE","ANGLE","75 x 75 x 6",0.990,6.8,1,6.73],
            ["SIDE BRACKET","FLAT","75 x 6",0.130,3.5,2,0.91],
            ["SUPPORT ANGLE","ANGLE","50 x 50 x 6",0.050,4.5,2,0.45],
            ["GUIDE BRACKET","FLAT","100 x 6",0.160,4.7,2,1.50],
            ["MOUNTING FLAT","FLAT","100 x 6",0.340,4.7,2,3.20],
        ]),
        1000: make_df([
            ["BASE CHANNEL","ISMC","125 x 65",1.334,12.7,1,16.94],
            ["BRG. ANGLE","ANGLE","90 x 90 x 6",1.194,8.2,1,9.79],
            ["SIDE BRACKET","FLAT","75 x 8",0.130,4.7,2,1.22],
            ["SUPPORT ANGLE","ANGLE","50 x 50 x 6",0.050,4.5,2,0.45],
            ["GUIDE BRACKET","FLAT","100 x 6",0.160,4.7,2,1.50],
            ["MOUNTING FLAT","FLAT","130 x 8",0.380,8.2,2,6.23],
        ]),
    }

    df = SARI_FRAME_STRUCTURES[nearest_bw]
    st.markdown("### Frame Fabrication Table (Editable)")
    edited_df = st.data_editor(df, use_container_width=True)
    TOTAL_FRAME_WEIGHT = edited_df["TOTAL WT"].sum()
    st.success(f"TOTAL FRAME WEIGHT = {round(TOTAL_FRAME_WEIGHT,2)} kg")

    guide_roller = st.number_input("Guide Roller Cost", value=400.0)
    pivot_bearing = st.number_input("Pivot Bearing Cost", value=1000.0)
    QTY = st.number_input("Frame QTY", value=1, step=1)

    RATE = 100
    UNIT_CP = TOTAL_FRAME_WEIGHT * RATE + guide_roller + pivot_bearing
    TOTAL_CP = UNIT_CP * QTY
    MARKUP = 1.25
    UNIT_PRICE = UNIT_CP * MARKUP
    TOTAL_PRICE = UNIT_PRICE * QTY

    if st.button("Add Frame Cost"):
        st.session_state.frame_costings.append({
            "DESCRIPTION": f"SARI FRAME {nearest_bw} MM",
            "FRAME_WT": round(TOTAL_FRAME_WEIGHT,2),
            "RATE": RATE,
            "UNIT_CP": round(UNIT_CP,2),
            "QTY": QTY,
            "TOTAL_CP": round(TOTAL_CP,2),
            "MARKUP": MARKUP,
            "UNIT_PRICE": round(UNIT_PRICE,2),
            "TOTAL_PRICE": round(TOTAL_PRICE,2)
        })
        st.session_state.stage = "frame_compiled"
        st.rerun()

# ---------------- FRAME COMPILED ----------------
if st.session_state.stage == "frame_compiled":
    st.subheader("Frame Costing Table")
    if len(st.session_state.frame_costings) > 0:
        df = pd.DataFrame(st.session_state.frame_costings)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No frame costing yet.")

    col1, col2, col3 = st.columns(3)

    if col1.button("Add More Frames"):
        if st.session_state.selected_roller == "SARI":
            st.session_state.stage = "frame_input_sari"
        else:
            st.session_state.stage = "frame_input"
        st.rerun()

    if col2.button("Back to Roller"):
        st.session_state.stage = "compiled"
        st.rerun()

    if col3.button("Download Frame Excel"):
        if len(st.session_state.frame_costings) > 0:
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="FRAME_COSTING")
            st.download_button("Download Frame Excel", buffer.getvalue(), file_name="frame_costing.xlsx")
        else:
            st.warning("No frame costing data to download.")

# ---------------- DOWNLOAD ROLLER ----------------
if len(st.session_state.costings) > 0:
    st.markdown("---")
    buffer = BytesIO()
    df = pd.DataFrame(st.session_state.costings)
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="ROLLER_COSTING")
    st.download_button("Download Roller Excel", buffer.getvalue(), file_name="roller_costing.xlsx")