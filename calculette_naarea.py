import streamlit as st

# Constantes
TAUX_CHARGES_SOCIALES = 0.23  # 23% de charges sociales (approximation Syntec) pour salaire normal
TAUX_ACTIVITE_PARTIELLE = 0.6  # 60% du salaire brut pour les jours en AP
VALEUR_TICKET_RESTO = 9.48    # Valeur faciale d'un ticket restaurant
PART_EMPLOYEUR_TR = 0.6       # 60% pris en charge par NAAREA
PART_SALARIE_TR = 0.4         # 40% à la charge du salarié
TAUX_CSG_AP = 0.062           # 6,20% CSG sur indemnité AP
TAUX_CRDS_AP = 0.005          # 0,50% CRDS sur indemnité AP
ABATTEMENT_FRAIS_PRO = 0.0175 # 1,75% abattement pour frais professionnels

# Initialize calculated flag
if "calculated" not in st.session_state:
    st.session_state.calculated = False

# Titre de l'application
st.title("Calculette NAAREA (Syntec) - Impact de l'Activité Partielle")

# Sous-titre
st.subheader("Entrez vos informations ci-dessus :")

# Entrées utilisateur avec Streamlit
salaire_brut_mensuel = st.number_input("Salaire brut mensuel initial (en €)", min_value=0.0, step=100.0, value=3000.0, key="salaire_brut_mensuel")
jour_travailles = st.number_input("Nombre de jour(s) travaill(e)s dans le mo(i)s", min_value=0.0, step=1.0, value=15.0, key="jour_travailles")
jour_activite_partielle = st.number_input("Nombre de jour(s) en activité partielle", min_value=0.0, step=1.0, value=5.0, key="jour_activite_partielle")
taux_imposition = st.number_input("Taux d'imposition (en %, ex. 10 pour 10%)", min_value=0.0, max_value=100.0, step=1.0, value=10.0, key="taux_iposition") / 100

# Buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("Calculer"):
        total_jours_ouvres = jour_travailles + jour_activite_partielle
        if total_jours_ouvres == 0:
            st.error("Erreur : Le total des jour(s) ouverts ne peut pas être 0.")
        else:
            # Calcul du salaire brut journalier
            salaire_brut_journalier = salaire_brut_mensuel / total_jours_ouvres
            # Salaire brut pour les jours travaillés
            salaire_brut_travail = jour_travailles * salaire_brut_journalier
            # Indemnité brute pour les jours en activité partielle
            indemnite_brute_ap = jour_activite_partielle * salaire_brut_journalier * TAUX_ACTIVITE_PARTIELLE
            # Salaire brut total
            salaire_brut_total = salaire_brut_travail + indemnite_brute_ap
            # Calcul du net pour les jours travaillés (avec charges sociales classiques)
            salaire_net_travail_avant_impot = salaire_brut_travail * (1 - TAUX_CHARGES_SOCIALES)
            # Calcul du net pour l’indemnité AP
            indemnite_ap_apres_abattement = indemnite_brute_ap * (1 - ABATTEMENT_FRAIS_PRO)
            csg_ap = indemnite_ap_apres_abattement * TAUX_CSG_AP
            crds_ap = indemnite_ap_apres_abattement * TAUX_CRDS_AP
            indemnite_nette_ap = indemnite_brute_ap - (csg_ap + crds_ap)
            # Salaire net avant impôt total (travail + AP)
            salaire_net_avant_impot = salaire_net_travail_avant_impot + indemnite_nette_ap
            # Calcul des tickets restaurant (uniquement pour jours travaillés)
            total_tr = jour_travailles * VALEUR_TICKET_RESTO
            part_salarie_tr = jour_travailles * VALEUR_TICKET_RESTO * PART_SALARIE_TR
            part_employeur_tr = jour_travailles * VALEUR_TICKET_RESTO * PART_EMPLOYEUR_TR
            # Salaire net avant impôt ajusté avec retenue TR
            salaire_net_avant_impot_avec_tr = salaire_net_avant_impot - part_salarie_tr
            # Salaire net après impôt (sans avantage TR)
            salaire_net_apres_impot = salaire_net_avant_impot_avec_tr * (1 - taux_iposition)
            # Revenu disponible avec avantage TR
            revenu_disponible_avec_tr = salaire_net_apres_impot + total_tr
            # Scénario sans activité partielle
            salaire_net_sans_ap = salaire_brut_mensuel * (1 - TAUX_CHARGES_SOCIALES)
            total_tr_sans_ap = total_jours_ouvres * VALEUR_TICKET_RESTO
            part_salarie_tr_sans_ap = total_jours_ouvres * VALEUR_TICKET_RESTO * PART_SALARIE_TR
            salaire_net_sans_ap_avec_tr = salaire_net_sans_ap - part_salarie_tr_sans_ap
            salaire_net_sans_ap_apres_impot = salaire_net_sans_ap_avec_tr * (1 - taux_iposition)
            revenu_disponible_sans_ap = salaire_net_sans_ap_apres_impot + total_tr_sans_ap
            # Calcul de la perte nette et du pourcentage
            perte_nette = revenu_disponible_sans_ap - revenu_disponible_avec_tr
            if revenu_disponible_sans_ap > 0:
                pourcentage_perte = (perte_nette / revenu_disponible_sans_ap) * 100
            else:
                pourcentage_perte = 0.0
            st.session_state.calculated = True
with col2:
    if st.button("Réinitialiser"):
        st.session_state.salaire_brut_mensuel = 3000.0
        st.session_state.jour_travailles = 15.0
        st.session_state.jour_activite_partielle = 5.0
        st.session_state.taux_iposition = 10.0
        st.session_state.calculated = False

# Display results if calculated
if st.session_state.get("calculated", False):
    st.subheader("Résultats :")
    st.write(f"**Salaire brut total :** {salaire_brut_total:.2f} €")
    st.write(f"- Dont salaire brut (jours travaillés) : {salaire_brut_travail:.2f} €")
    st.write(f"- Dont indemnité brute AP : {indemnite_brute_ap:.2f} €")
    st.write(f"**Salaire net avant impôt :** {salaire_net_avant_impot_avec_tr:.2f} €")
    st.write(f"**Salaire net après impôt (sans TR) :** {salaire_net_apres_impot:.2f} €")
    st.write(f"**Valeur totale des tickets restaurant :** {total_tr:.2f} € (dont {part_employeur_tr:.2f} € par NAAREA)")
    st.write(f"**Revenu disponible (net après impôt + TR) :** {revenu_disponible_avec_tr:.2f} €")
    st.write(f"**Revenu disponible sans activité partielle :** {revenu_disponible_sans_ap:.2f} €")
    st.write(f"**Perte nette due à l'activité partielle :** {perte_nette:.2f} €")
    st.write(f"**Pourcentage de revenu perdu :** {pourcentage_perte:.2f} %")

# Informations supplémentaires
st.sidebar.header("À propos")
st.sidebar.write("""
Cette calculette est conçue pour les salariés de NAAREA sous la convention Syntec.  
Elle estime l'impact de l'activité partielle (AP) sur le revenu disponible.  
Hypothèses :  
- Charges sociales : 23% (salaire normal).  
- Indemnité AP : 60% du brut, soumise à CSG 6,20% + CRDS 0,50% après abattement 1,75%.  
- TR : 9,48 €/jour travaillé, 60% pris en charge par NAAREA.  
Contactez votre RH pour des données spécifiques.
""")
