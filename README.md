# Morocco Business Suite

Suite de gestion marocaine basee sur Odoo Community 18, avec une couche metier independante pour la gestion commerciale, la comptabilite, les controles, les etats financiers, la facturation electronique et les marches/appels d'offres.

## Phase 1

Objectif fonctionnel prioritaire :

1. Societe marocaine
2. Clients / fournisseurs
3. Articles / services
4. Devis -> Commande -> Livraison -> Facture -> Reglement
5. Achats -> Reception -> Facture fournisseur -> Reglement
6. Comptabilisation automatique
7. Balance, grand livre, journaux et situation tiers
8. Preparation e-facturation Maroc
9. Architecture module Marches / Appels d'offres

## Architecture

Le coeur Odoo Community n'est pas modifie. Les adaptations sont isolees dans `addons/mbs_*` afin de faciliter les mises a jour et de garder la marque et la logique metier independantes.

## Demarrage local

```bash
docker compose up -d
```

Odoo : http://localhost:8069

> Projet en cours de construction. Les fonctions fiscales et reglementaires devront etre validees sur les specifications officielles avant utilisation en production.
