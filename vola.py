import streamlit as st
import os
import fitz  # PyMuPDF
from PIL import Image
import io

st.set_page_config(page_title="PromoLocal Visivo", page_icon="🛒", layout="centered")

st.title("🛒 PromoLocal Visivo")
st.write("Inserisci un prodotto per vedere l'immagine dell'offerta")

CARTELLA_VOLANTINI = os.path.join("static", "volantini")
if not os.path.exists(CARTELLA_VOLANTINI):
    os.makedirs(CARTELLA_VOLANTINI)

def cerca_e_ritaglia_prodotto(termine_ricerca):
    risultati = []
    if not os.path.exists(CARTELLA_VOLANTINI):
        return risultati
        
    file_pdf = [f for f in os.listdir(CARTELLA_VOLANTINI) if f.endswith('.pdf')]
    
    for nome_file in file_pdf:
        percorso_completo = os.path.join(CARTELLA_VOLANTINI, nome_file)
        try:
            doc = fitz.open(percorso_completo)
            
            for num_pagina in range(len(doc)):
                pagina = doc[num_pagina]
                rettangoli_testo = pagina.search_for(termine_ricerca)
                
                for rect in rettangoli_testo:
                    # RITAGLIO AMPIO: Aumentiamo la tolleranza per prendere l'intero blocco offerta
                    # Estendiamo molto a destra/sinistra (250px) e sopra/sotto (180px)
                    clip_rect = fitz.Rect(
                        max(0, rect.x0 - 250),
                        max(0, rect.y0 - 180),
                        min(pagina.rect.width, rect.x1 + 250),
                        min(pagina.rect.height, rect.y1 + 180)
                    )
                    
                    # RISOLUZIONE: Aumentiamo la matrice a (2.5, 2.5) per rendere i testi piccoli nitidissimi
                    matrice = fitz.Matrix(2.5, 2.5) 
                    pix = pagina.get_pixmap(matrix=matrice, clip=clip_rect)
                    
                    img_data = pix.tobytes("png")
                    immagine_pil = Image.open(io.BytesIO(img_data))
                    
                    risultati.append({
                        "supermercato": nome_file.replace(".pdf", "").upper(),
                        "pagina": num_pagina + 1,
                        "immagine": immagine_pil
                    })
                    break
        except Exception as e:
            pass
            
    return risultati

# Interfaccia Utente
prodotto_cercato = st.text_input("🔍 Quale prodotto vuoi cercare?", placeholder="es. Latte, Caffè, Pasta...")

if prodotto_cercato:
    st.markdown(f"### 🖼️ Offerte visive trovate per: *{prodotto_cercato}*")
    
    with st.spinner("Scansione e ritaglio in corso..."):
        offerte = cerca_e_ritaglia_prodotto(prodotto_cercato)
    
    if offerte:
        for offerta in offerte:
            with st.container():
                st.markdown(f"🏪 **{offerta['supermercato']}** — Pagina {offerta['pagina']}")
                
                # Mostriamo la foto del volantino a schermo intero sul telefono
                st.image(offerta['immagine'], use_container_width=True)
                st.markdown("---")
    else:
        st.warning("Nessun prodotto trovato nei volantini attuali.")
else:
    st.write("---")
    st.write("🏪 **Volantini pronti nel database locale:**")
    if os.path.exists(CARTELLA_VOLANTINI):
        file_presenti = [f for f in os.listdir(CARTELLA_VOLANTINI) if f.endswith('.pdf')]
        if file_presenti:
            for f in file_presenti:
                st.success(f"✅ {f.replace('.pdf', '').upper()}")