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

# Barème progressif de l'impôt sur le revenu 2024
TRANCHES_IR = [
    (10777, 0.0),
    (27478, 0.11),
    (78570, 0.30),
    (168994, 0.41),
    (float("inf"), 0.45)
]

def calcul_impot(revenu_net_imposable, quotient_familial):
    revenu_par_part = revenu_net_imposable / quotient_familial
    impot = 0
    tranche_precedente = 0
    
    for tranche, taux in TRANCHES_IR:
        if revenu_par_part > tranche:
            impot += (tranche - tranche_precedente) * taux
            tranche_precedente = tranche
        else:
            impot += (revenu_par_part - tranche_precedente) * taux
            break
    
    return impot * quotient_familial

# Titre de l'application
st.title("Calculette NAAREA (Syntec) - Impact de l'Activité Partielle")

# Entrées utilisateur
salaire_brut_mensuel = st.number_input("Salaire brut mensuel initial (en €)", min_value=0.0, step=100.0, value=3000.0)
jours_travailles = st.number_input("Nombre de jours travaillés dans le mois", min_value=0.0, step=1.0, value=15.0)
jours_activite_partielle = st.number_input("Nombre de jours en activité partielle", min_value=0.0, step=1.0, value=5.0)
coefficient_familial = st.number_input("Nombre de parts fiscales (quotient familial)", min_value=1.0, step=0.5, value=1.0)

# Calcul du total des jours ouvrés
total_jours_ouvres = jours_travailles + jours_activite_partielle

# Bouton pour lancer le calcul
if st.button("Calculer"):
    if total_jours_ouvres == 0:
        st.error("Erreur : Le total des jours ouvrés ne peut pas être 0.")
    else:
        salaire_brut_journalier = salaire_brut_mensuel / total_jours_ouvres
        salaire_brut_travail = jours_travailles * salaire_brut_journalier
        indemnite_brute_ap = jours_activite_partielle * salaire_brut_journalier * TAUX_ACTIVITE_PARTIELLE
        salaire_brut_total = salaire_brut_travail + indemnite_brute_ap

        salaire_net_travail_avant_impot = salaire_brut_travail * (1 - TAUX_CHARGES_SOCIALES)
        indemnite_ap_apres_abattement = indemnite_brute_ap * (1 - ABATTEMENT_FRAIS_PRO)
        csg_ap = indemnite_ap_apres_abattement * TAUX_CSG_AP
        crds_ap = indemnite_ap_apres_abattement * TAUX_CRDS_AP
        indemnite_nette_ap = indemnite_brute_ap - (csg_ap + crds_ap)
        salaire_net_avant_impot = salaire_net_travail_avant_impot + indemnite_nette_ap

        total_tr = jours_travailles * VALEUR_TICKET_RESTO
        part_salarie_tr = jours_travailles * VALEUR_TICKET_RESTO * PART_SALARIE_TR
        part_employeur_tr = jours_travailles * VALEUR_TICKET_RESTO * PART_EMPLOYEUR_TR
        salaire_net_avant_impot_avec_tr = salaire_net_avant_impot - part_salarie_tr

        revenu_imposable = salaire_net_avant_impot_avec_tr * 12  # Annuel
        impot = calcul_impot(revenu_imposable, coefficient_familial)
        salaire_net_apres_impot = salaire_net_avant_impot_avec_tr - (impot / 12)  # Mensuel
        revenu_disponible_avec_tr = salaire_net_apres_impot + total_tr

        st.subheader("Résultats :")
        st.write(f"**Salaire brut total :** {salaire_brut_total:.2f} €")
        st.write(f"**Salaire net avant impôt :** {salaire_net_avant_impot_avec_tr:.2f} €")
        st.write(f"**Impôt estimé (annuel) :** {impot:.2f} €")
        st.write(f"**Salaire net après impôt :** {salaire_net_apres_impot:.2f} €")
        st.write(f"**Valeur totale des tickets restaurant :** {total_tr:.2f} €")
        st.write(f"**Revenu disponible (net après impôt + TR) :** {revenu_disponible_avec_tr:.2f} €")
