# Morocco Business Suite

Suite de gestion marocaine basee sur Odoo Community 18. Le coeur Odoo n'est pas modifie : toute la logique MBS reste dans des modules separes `addons/mbs_*`.

## Modules disponibles

- `mbs_core` : identite marocaine societe/tiers (ICE, IF, RC, CNSS, patente, exercice) et menu principal.
- `mbs_commercial` : clients, fournisseurs, produits, ventes, achats, stock et controles metier.
- `mbs_accounting` : controles factures, situation entreprise, creances/dettes et assistant de rapports comptables.
- `mbs_einvoice` : preparation d'une facture electronique structuree, versionnee et prete a recevoir le futur connecteur officiel.
- `mbs_tenders` : appels d'offres, marches, bordereau des prix, situations/decomptes, retenues, avances et penalites.

## Demarrage local

Prerequis : Docker Desktop ou Docker Engine + Compose.

```bash
git clone https://github.com/PRINCESOON2021/Morocco-Business-Suite.git
cd Morocco-Business-Suite
docker compose up -d
```

Ouvrir ensuite : `http://localhost:8069`

Creer une base Odoo en choisissant le Maroc comme pays, puis activer le mode developpeur si necessaire et mettre a jour la liste des applications.

Installer dans cet ordre :

1. MBS Core Maroc
2. MBS Gestion Commerciale Maroc
3. MBS Comptabilite Maroc
4. MBS Facturation Electronique Maroc
5. MBS Marches et Appels d'Offres Maroc

Les dependances Odoo standard (ventes, achats, stock, comptabilite et localisation Maroc) sont installees automatiquement par Odoo.

## Parcours de test V1

### Gestion commerciale

1. Creer un client societe avec ICE/IF/RC.
2. Creer un produit et son prix.
3. Creer un devis, le confirmer et effectuer la livraison.
4. Generer la facture client et enregistrer le reglement.
5. Verifier que la facture et les ecritures comptables sont generees par Odoo.
6. Tester une commande avec ICE manquant ou ligne invalide : elle doit apparaitre dans `Ventes a verifier`.

### Achats

1. Creer un fournisseur.
2. Creer et confirmer une commande fournisseur.
3. Enregistrer la reception.
4. Creer la facture fournisseur et son paiement.
5. Verifier `Achats a verifier` et `Dettes fournisseurs`.

### Comptabilite / controle

- Ouvrir `Morocco Business Suite > Situation de mon entreprise`.
- Verifier CA facture, creances, dettes et retards clients.
- Ouvrir `Comptabilite Maroc > Centre de controle`.
- Tester l'assistant `Rapports` pour Balance, Grand livre, Clients, Fournisseurs, Creances, Dettes et TVA.

### Facturation electronique

Sur une facture client validee, utiliser `Preparer e-facture`. Le module genere un payload structure avec vendeur, acheteur, ICE/IF/RC, devise, montants, taxes et lignes. Le schema est volontairement marque `pending-official-spec` tant que la specification officielle definitive n'est pas integree.

### Marches / Appels d'offres

Tester le flux :

`Appel d'offres -> Marche -> Bordereau des prix -> Situation/Decompte -> Retenue/Avance/Penalite -> Facture liee`

Le module ne genere pas encore automatiquement la facture du decompte afin d'eviter de poster des deductions fiscales/comptables non validees. Cette automatisation sera ajoutee apres validation des regles metier.

## Validation technique

Le depot contient `.github/workflows/validate.yml` pour controler a chaque push :

- syntaxe Python ;
- validite XML ;
- structure minimale des manifests Odoo.

## Important

Cette V1 est une base fonctionnelle de developpement. Les etats fiscaux, la TVA, la facturation electronique et les regles des marches publics doivent etre valides sur les textes/specifications officielles avant une utilisation en production.
