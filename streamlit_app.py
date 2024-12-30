# Credit: This app is inspired by https://huggingface.co/spaces/osanseviero/esmfold

import streamlit as st
from stmol import showmol
import py3Dmol
import requests
import biotite.structure.io as bsio

# Set up the sidebar and app title
st.sidebar.title('🔮 ProtiGenie')
st.sidebar.write('[*ProtiGenie*](https://esmatlas.com/about) is an end-to-end single-sequence protein structure predictor powered by the ESM-2 language model.')

# Function to visualize protein structure
def render_molecule(pdb):
    pdb_view = py3Dmol.view()
    pdb_view.addModel(pdb, 'pdb')
    pdb_view.setStyle({'cartoon': {'color': 'spectrum'}})
    pdb_view.setBackgroundColor('white')
    pdb_view.zoomTo()
    pdb_view.zoom(2, 800)
    pdb_view.spin(True)
    showmol(pdb_view, height=500, width=800)

# Protein sequence input
DEFAULT_SEQUENCE = (
    "MGSSHHHHHHSSGLVPRGSHMRGPNPTAASLEASAGPFTVRSFTVSRPSGYGAGTVYYPTNAGGTVGAIAIVPGYTARQSSIKWWGPRLASHGFVVITIDTNSTLD"
    "QPSSRSSQQMAALRQVASLNGTSSSPIYGKVDTARMGVMGWSMGGGGSLISAANNPSLKAAAPQAPWDSSTNFSSVTVPTLIFACENDSIAPVNSSALPIYDSMSR"
    "NAKQFLEINGGSHSCANSGNSNQALIGKKGVAWMKRFMDNDTRYSTFACENPNSTRVSDFRTANCSLEDPAANKARKEAELAAATAEQ"
)
protein_sequence = st.sidebar.text_area('Input Protein Sequence', DEFAULT_SEQUENCE, height=275)

# Function to predict protein structure using ESMFold
def predict_structure(sequence=protein_sequence):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post('https://api.esmatlas.com/foldSequence/v1/pdb/', headers=headers, data=sequence)
    
    pdb_content = response.content.decode('utf-8')
    with open('predicted_structure.pdb', 'w') as pdb_file:
        pdb_file.write(pdb_content)

    structure = bsio.load_structure('predicted_structure.pdb', extra_fields=["b_factor"])
    average_b_factor = round(structure.b_factor.mean(), 4)

    # Visualization
    st.subheader('Visualization of Predicted Protein Structure')
    render_molecule(pdb_content)

    # plDDT confidence score
    st.subheader('plDDT Confidence Score')
    st.write('plDDT is a per-residue estimate of the prediction confidence on a scale of 0-100.')
    st.info(f'plDDT: {average_b_factor}')

    # Download button for PDB file
    st.download_button(
        label="Download PDB File",
        data=pdb_content,
        file_name='predicted_structure.pdb',
        mime='text/plain',
    )

# Button for prediction
predict_button = st.sidebar.button('Predict', on_click=predict_structure)

if not predict_button:
    st.warning('👈 Please input a protein sequence and click Predict!')
