import streamlit as st
import os
import fitz  # Importa PyMuPDF
from PIL import Image
import io

st.set_page_config(page_title="PromoLocal Visivo", page_icon="🛒", layout="centered")

st.title("🛒 PromoLocal Visivo")
st.write("Inserisci un prodotto per vedere l'immagine dell'offerta sul volantino")

# Cartella dei volantini (puoi rimetterla dove vuoi, anche fuori da static)
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
            # Apriamo il PDF con PyMuPDF
            doc = fitz.open(percorso_completo)
            
            for num_pagina in range(len(doc)):
                pagina = doc[num_pagina]
                # Cerchiamo la parola esatta nella pagina
                rettangoli_testo = pagina.search_for(termine_ricerca)
                
                # Se la parola viene trovata, ritagliamo la zona circostante
                for rect in rettangoli_testo:
                    # Allarghiamo il rettangolo di ritaglio per catturare anche il prezzo vicino
                    # Aggiungiamo 120 pixel a destra e sinistra, 80 sopra e sotto
                    clip_rect = fitz.Rect(
                        max(0, rect.x0 - 120),
                        max(0, rect.y0 - 80),
                        min(pagina.rect.width, rect.x1 + 120),
                        min(pagina.rect.height, rect.y1 + 80)
                    )
                    
                    # Trasformiamo solo quel pezzetto di pagina in un'immagine ad alta definizione
                    matrice = fitz.Matrix(2, 2) # Raddoppia la qualità per leggere bene i prezzi
                    pix = pagina.get_pixmap(matrix=matrice, clip=clip_rect)
                    
                    # Convertiamo i dati in un'immagine leggibile da Streamlit
                    img_data = pix.tobytes("png")
                    immagine_pil = Image.open(io.BytesIO(img_data))
                    
                    risultati.append({
                        "supermercato": nome_file.replace(".pdf", "").upper(),
                        "pagina": num_pagina + 1,
                        "immagine": immagine_pil
                    })
                    # Per non duplicare troppi ritagli uguali della stessa pagina, passiamo alla successiva
                    break
        except Exception as e:
            pass
            
    return risultati

# Interfaccia Utente
prodotto_cercato = st.text_input("🔍 Quale prodotto vuoi cercare visivamente?", placeholder="es. Latte, Caffè, Pasta...")

if prodotto_cercato:
    st.markdown(f"### 🖼️ Offerte visive trovate per: *{prodotto_cercato}*")
    
    with st.spinner("Scansione visiva e ritaglio dei volantini..."):
        offerte = cerca_e_ritaglia_prodotto(prodotto_cercato)
    
    if offerte:
        for offerta in offerte:
            # Creiamo una scheda grafica pulita per ogni ritaglio
            with st.container():
                st.markdown(f"🏪 **{offerta['supermercato']}** — Pagina {offerta['pagina']}")
                # Mostriamo la foto reale estratta dal volantino!
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