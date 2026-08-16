#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
corpus_facturx.py — générateur d'un corpus public de cas limites Factur-X.

Produit des factures Factur-X volontairement défectueuses, une par défaut,
avec pour chacune la référence à la règle violée et le comportement attendu
d'un validateur conforme.

    python3 corpus_facturx.py list                 # catalogue des cas
    python3 corpus_facturx.py generate --out ./corpus
    python3 corpus_facturx.py manifest --out ./corpus

Chaque cas produit un dossier contenant la facture PDF, le XML seul, et une
fiche décrivant le défaut. Un manifeste global récapitule l'ensemble.

USAGE PRÉVU
Ce corpus sert à tester sa propre implémentation, ou une implémentation
publique et librement accessible. Ne jamais soumettre ces fichiers au système
de production d'un tiers sans y avoir été invité par écrit.

LIMITES ASSUMÉES — à lire avant de publier quoi que ce soit
La conformité PDF/A-3 produite ici est approchée : le profil ICC n'est pas
embarqué et les polices ne sont pas intégralement souscrites. Les fichiers
sont donc valides pour tester l'extraction et la validation du XML, mais ne
doivent pas servir de référence de conformité PDF/A-3. Les cas marqués
`pdfa_approximatif` le signalent explicitement.
"""

import argparse
import copy
import hashlib
import json
import os
import shutil
import sys
from dataclasses import dataclass, field
from datetime import date
from typing import Callable, Optional

# ---------------------------------------------------------------------------
# Facture de référence — Factur-X BASIC, conforme EN 16931
# ---------------------------------------------------------------------------

NS = {
    "rsm": "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100",
    "ram": "urn:un:unece:uncefact:data:standard:"
           "ReusableAggregateBusinessInformationEntity:100",
    "udt": "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100",
}

PROFIL_BASIC = "urn:cen.eu:en16931:2017#compliant#urn:factur-x.eu:1p0:basic"
PROFIL_MINIMUM = "urn:factur-x.eu:1p0:minimum"
PROFIL_EN16931 = "urn:cen.eu:en16931:2017"

# Ressources PDF/A-3. Adapter si absentes du système.
CHEMIN_POLICE = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
CHEMIN_POLICE_GRAS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CHEMIN_ICC = "/usr/share/texlive/texmf-dist/tex/generic/colorprofiles/sRGB.icc"


def facture_reference():
    """Modèle de la facture saine.

    Conforme EN 16931 ET au profil français BR-FR (AFNOR FE-XP Z12-012),
    qui ajoute des obligations absentes de la norme européenne : mentions
    légales PMD/PMT/AAB, mode de facturation, adresses électroniques, et
    surtout SIREN à 9 chiffres et non SIRET pour schemeID 0002.
    """
    return {
        "profil": PROFIL_BASIC,
        "mode_facturation": "S1",     # BT-23 — prestation de services, cas 1
        "numero": "FA-2026-0001",
        "type_code": "380",
        "date_emission": "20260815",
        "date_format": "102",
        "date_livraison": "20260831",
        "devise": "EUR",
        "notes": [
            # BR-FR-05 : les trois mentions légales françaises obligatoires
            ("PMD", "En cas de retard de paiement, taux d'intérêt égal à "
                    "trois fois le taux d'intérêt légal."),
            ("PMT", "Indemnité forfaitaire pour frais de recouvrement : "
                    "40 euros."),
            ("AAB", "Aucun escompte accordé pour paiement anticipé."),
        ],
        "vendeur": {
            "nom": "Atelier Berthier SARL",
            "siren": "392809137",          # BT-30 — 9 chiffres, schemeID 0002
            "siret": "39280913700027",     # informatif, hors BT-30
            "tva": "FR40392809137",
            "endpoint": "39280913700027",  # BT-34 — adresse électronique
            "endpoint_scheme": "0225",     # SIRET comme point de routage
            "adresse": "14 rue des Fabriques",
            "cp": "45000",
            "ville": "Orleans",
            "pays": "FR",
        },
        "acheteur": {
            "nom": "Communaute de communes du Val de Loire",
            "siren": "244500011",
            "siret": "24450001100015",
            "tva": None,
            "endpoint": "24450001100015",  # BT-49
            "endpoint_scheme": "0225",
            "adresse": "2 place de la Mairie",
            "cp": "41000",
            "ville": "Blois",
            "pays": "FR",
        },
        "lignes": [
            {"id": "1", "designation": "Maintenance preventive CVC - aout 2026",
             "quantite": "1.00", "unite": "C62",
             "prix_unitaire": "2400.00", "montant_ht": "2400.00",
             "taux_tva": "20.00", "categorie_tva": "S"},
            {"id": "2", "designation": "Deplacement technicien",
             "quantite": "3.00", "unite": "C62",
             "prix_unitaire": "45.00", "montant_ht": "135.00",
             "taux_tva": "20.00", "categorie_tva": "S"},
        ],
        "echeance": "20260914",
        "moyen_paiement": "30",
        "iban": "FR7630006000011234567890189",
    }


def _nombre(v):
    """Parse un montant même mal écrit. Le défaut reste dans le XML sérialisé :
    on veut produire le fichier fautif, pas planter dessus."""
    try:
        return float(str(v).replace(" ", "").replace(",", "."))
    except (ValueError, TypeError):
        return 0.0


def totaux(f):
    """Calcule les totaux à partir des lignes. Les cas peuvent les écraser."""
    ht = sum(_nombre(l["montant_ht"]) for l in f["lignes"])
    par_taux = {}
    for l in f["lignes"]:
        cle = (l["categorie_tva"], l["taux_tva"])
        par_taux[cle] = par_taux.get(cle, 0.0) + _nombre(l["montant_ht"])
    tva = sum(round(base * _nombre(taux) / 100, 2)
              for (_, taux), base in par_taux.items())
    return {
        "lignes_ht": round(ht, 2),
        "total_ht": round(ht, 2),
        "total_tva": round(tva, 2),
        "total_ttc": round(ht + tva, 2),
        "net_a_payer": round(ht + tva, 2),
        "ventilation": [
            {"categorie": cat, "taux": taux, "base": round(base, 2),
             "montant": round(base * _nombre(taux) / 100, 2)}
            for (cat, taux), base in par_taux.items()
        ],
    }


def bloc_partie(p, balise):
    x = [f"      <ram:{balise}>",
         f"        <ram:Name>{p['nom']}</ram:Name>"]
    if p.get("siren"):
        # BT-30 / BR-FR-32 : schemeID 0002 = SIREN, 9 chiffres. Pas le SIRET.
        x += ["        <ram:SpecifiedLegalOrganization>",
              f'          <ram:ID schemeID="0002">{p["siren"]}</ram:ID>',
              "        </ram:SpecifiedLegalOrganization>"]
    x += ["        <ram:PostalTradeAddress>",
          f"          <ram:PostcodeCode>{p['cp']}</ram:PostcodeCode>",
          f"          <ram:LineOne>{p['adresse']}</ram:LineOne>",
          f"          <ram:CityName>{p['ville']}</ram:CityName>",
          f"          <ram:CountryID>{p['pays']}</ram:CountryID>",
          "        </ram:PostalTradeAddress>"]
    if p.get("endpoint"):
        # BT-34 (vendeur) / BT-49 (acheteur) — obligatoires en profil français
        x += ["        <ram:URIUniversalCommunication>",
              f'          <ram:URIID schemeID="{p.get("endpoint_scheme", "0225")}">'
              f'{p["endpoint"]}</ram:URIID>',
              "        </ram:URIUniversalCommunication>"]
    if p.get("tva"):
        x += ["        <ram:SpecifiedTaxRegistration>",
              f'          <ram:ID schemeID="VA">{p["tva"]}</ram:ID>',
              "        </ram:SpecifiedTaxRegistration>"]
    x.append(f"      </ram:{balise}>")
    return "\n".join(x)


def construire_xml(f, t=None):
    """Sérialise le modèle en CII. Volontairement en texte : les cas doivent
    pouvoir produire du XML invalide, ce qu'une bibliothèque interdirait."""
    t = t or totaux(f)
    lignes = []
    for l in f["lignes"]:
        lignes.append(f"""    <ram:IncludedSupplyChainTradeLineItem>
      <ram:AssociatedDocumentLineDocument>
        <ram:LineID>{l['id']}</ram:LineID>
      </ram:AssociatedDocumentLineDocument>
      <ram:SpecifiedTradeProduct>
        <ram:Name>{l['designation']}</ram:Name>
      </ram:SpecifiedTradeProduct>
      <ram:SpecifiedLineTradeAgreement>
        <ram:NetPriceProductTradePrice>
          <ram:ChargeAmount>{l['prix_unitaire']}</ram:ChargeAmount>
        </ram:NetPriceProductTradePrice>
      </ram:SpecifiedLineTradeAgreement>
      <ram:SpecifiedLineTradeDelivery>
        <ram:BilledQuantity unitCode="{l['unite']}">{l['quantite']}</ram:BilledQuantity>
      </ram:SpecifiedLineTradeDelivery>
      <ram:SpecifiedLineTradeSettlement>
        <ram:ApplicableTradeTax>
          <ram:TypeCode>VAT</ram:TypeCode>
          <ram:CategoryCode>{l['categorie_tva']}</ram:CategoryCode>
          <ram:RateApplicablePercent>{l['taux_tva']}</ram:RateApplicablePercent>
        </ram:ApplicableTradeTax>
        <ram:SpecifiedTradeSettlementLineMonetarySummation>
          <ram:LineTotalAmount>{l['montant_ht']}</ram:LineTotalAmount>
        </ram:SpecifiedTradeSettlementLineMonetarySummation>
      </ram:SpecifiedLineTradeSettlement>
    </ram:IncludedSupplyChainTradeLineItem>""")

    ventil = []
    for v in t["ventilation"]:
        ventil.append(f"""      <ram:ApplicableTradeTax>
        <ram:CalculatedAmount>{v['montant']:.2f}</ram:CalculatedAmount>
        <ram:TypeCode>VAT</ram:TypeCode>
        <ram:BasisAmount>{v['base']:.2f}</ram:BasisAmount>
        <ram:CategoryCode>{v['categorie']}</ram:CategoryCode>
        <ram:RateApplicablePercent>{v['taux']}</ram:RateApplicablePercent>
      </ram:ApplicableTradeTax>""")

    devise = (f"      <ram:InvoiceCurrencyCode>{f['devise']}"
              f"</ram:InvoiceCurrencyCode>\n") if f.get("devise") else ""

    # BR-FR-05 : mentions légales françaises obligatoires
    notes = "\n".join(
        f"""    <ram:IncludedNote>
      <ram:Content>{txt}</ram:Content>
      <ram:SubjectCode>{code}</ram:SubjectCode>
    </ram:IncludedNote>"""
        for code, txt in f.get("notes", []))
    if notes:
        notes += "\n"

    # BR-FR-08 : mode de facturation
    processus = (f"""    <ram:BusinessProcessSpecifiedDocumentContextParameter>
      <ram:ID>{f['mode_facturation']}</ram:ID>
    </ram:BusinessProcessSpecifiedDocumentContextParameter>\n"""
                 if f.get("mode_facturation") else "")

    # PEPPOL-R008 : pas d'élément vide
    livraison = (f"""    <ram:ApplicableHeaderTradeDelivery>
      <ram:ActualDeliverySupplyChainEvent>
        <ram:OccurrenceDateTime>
          <udt:DateTimeString format="102">{f['date_livraison']}</udt:DateTimeString>
        </ram:OccurrenceDateTime>
      </ram:ActualDeliverySupplyChainEvent>
    </ram:ApplicableHeaderTradeDelivery>"""
                 if f.get("date_livraison")
                 else "    <ram:ApplicableHeaderTradeDelivery/>")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rsm:CrossIndustryInvoice xmlns:rsm="{NS['rsm']}" xmlns:ram="{NS['ram']}" xmlns:udt="{NS['udt']}">
  <rsm:ExchangedDocumentContext>
{processus}    <ram:GuidelineSpecifiedDocumentContextParameter>
      <ram:ID>{f['profil']}</ram:ID>
    </ram:GuidelineSpecifiedDocumentContextParameter>
  </rsm:ExchangedDocumentContext>
  <rsm:ExchangedDocument>
    <ram:ID>{f['numero']}</ram:ID>
    <ram:TypeCode>{f['type_code']}</ram:TypeCode>
    <ram:IssueDateTime>
      <udt:DateTimeString format="{f['date_format']}">{f['date_emission']}</udt:DateTimeString>
    </ram:IssueDateTime>
{notes}  </rsm:ExchangedDocument>
  <rsm:SupplyChainTradeTransaction>
{chr(10).join(lignes)}
    <ram:ApplicableHeaderTradeAgreement>
{bloc_partie(f['vendeur'], 'SellerTradeParty')}
{bloc_partie(f['acheteur'], 'BuyerTradeParty')}
    </ram:ApplicableHeaderTradeAgreement>
{livraison}
    <ram:ApplicableHeaderTradeSettlement>
{devise}{chr(10).join(ventil)}
      <ram:SpecifiedTradePaymentTerms>
        <ram:DueDateDateTime>
          <udt:DateTimeString format="102">{f['echeance']}</udt:DateTimeString>
        </ram:DueDateDateTime>
      </ram:SpecifiedTradePaymentTerms>
      <ram:SpecifiedTradeSettlementHeaderMonetarySummation>
        <ram:LineTotalAmount>{t['lignes_ht']:.2f}</ram:LineTotalAmount>
        <ram:TaxBasisTotalAmount>{t['total_ht']:.2f}</ram:TaxBasisTotalAmount>
        <ram:TaxTotalAmount currencyID="{f.get('devise') or 'EUR'}">{t['total_tva']:.2f}</ram:TaxTotalAmount>
        <ram:GrandTotalAmount>{t['total_ttc']:.2f}</ram:GrandTotalAmount>
        <ram:DuePayableAmount>{t['net_a_payer']:.2f}</ram:DuePayableAmount>
      </ram:SpecifiedTradeSettlementHeaderMonetarySummation>
    </ram:ApplicableHeaderTradeSettlement>
  </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>
"""


# ---------------------------------------------------------------------------
# Fabrication du PDF porteur
# ---------------------------------------------------------------------------

def construire_pdf(xml_bytes, f, chemin, options=None):
    """PDF lisible + XML embarqué. `options` déclenche les défauts PDF."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import pikepdf

    # PDF/A-3 exige des polices embarquées : Helvetica (base 14) ne l'est
    # jamais. On souscrit DejaVu, présente sur la plupart des systèmes.
    police, police_g = "Helvetica", "Helvetica-Bold"
    for base, gras in ((CHEMIN_POLICE, CHEMIN_POLICE_GRAS),):
        if base and os.path.exists(base):
            try:
                pdfmetrics.registerFont(TTFont("Corpus", base))
                pdfmetrics.registerFont(TTFont("Corpus-Bold", gras))
                police, police_g = "Corpus", "Corpus-Bold"
            except Exception:
                pass

    o = options or {}
    tmp = chemin + ".tmp"
    t = totaux(f)

    c = rl_canvas.Canvas(tmp, pagesize=A4, initialFontName=police,
                         initialFontSize=9)
    # Neutralise l'en-tête « BT /F1 12 Tf ET » que ReportLab émet d'office
    # avec la police par défaut, seule référence résiduelle à Helvetica.
    c.setFont(police, 9)
    L, H = A4
    c.setFont(police_g, 15)
    c.drawString(20 * mm, H - 25 * mm, "FACTURE")
    c.setFont(police, 9)
    c.drawString(20 * mm, H - 32 * mm, f"N° {f['numero']}")
    c.drawString(20 * mm, H - 37 * mm,
                 f"Date : {f['date_emission']}  ·  Échéance : {f['echeance']}")

    y = H - 50 * mm
    for titre, p in (("Émetteur", f["vendeur"]), ("Destinataire", f["acheteur"])):
        c.setFont(police_g, 9)
        c.drawString(20 * mm, y, titre)
        c.setFont(police, 9)
        for i, ligne in enumerate((p["nom"], p["adresse"],
                                   f"{p['cp']} {p['ville']}",
                                   f"SIRET {p.get('siret') or '—'}")):
            c.drawString(20 * mm, y - (i + 1) * 5 * mm, str(ligne))
        y -= 32 * mm

    c.setFont(police_g, 9)
    c.drawString(20 * mm, y, "Désignation")
    c.drawRightString(150 * mm, y, "Qté")
    c.drawRightString(190 * mm, y, "Montant HT")
    y -= 6 * mm
    c.setFont(police, 9)
    for l in f["lignes"]:
        c.drawString(20 * mm, y, l["designation"][:60])
        c.drawRightString(150 * mm, y, l["quantite"])
        c.drawRightString(190 * mm, y, f"{l['montant_ht']} €")
        y -= 5 * mm

    y -= 6 * mm
    c.setFont(police_g, 10)
    for lib, val in (("Total HT", t["total_ht"]), ("TVA", t["total_tva"]),
                     ("Total TTC", t["total_ttc"])):
        c.drawRightString(160 * mm, y, lib)
        c.drawRightString(190 * mm, y, f"{val:.2f} €")
        y -= 5.5 * mm

    c.setFont(police, 7)
    c.drawString(20 * mm, 15 * mm,
                 "Corpus de test Factur-X — document fictif, sans valeur légale.")
    c.showPage()
    c.save()

    pdf = pikepdf.open(tmp)

    # ReportLab déclare Helvetica dans les ressources même si aucun texte ne
    # l'utilise. Une police base-14 non embarquée suffit à faire échouer
    # PDF/A-3 : on retire les entrées non référencées par le flux de contenu.
    if not o.get("sans_pdfa"):
        for page in pdf.pages:
            polices = page.Resources.get("/Font")
            if not polices:
                continue
            contenu = b"".join(bytes(s.read_bytes())
                               for s in ([page.Contents]
                                         if not isinstance(page.Contents,
                                                           pikepdf.Array)
                                         else page.Contents))
            for nom in [str(k) for k in polices.keys()]:
                if nom.encode() not in contenu:
                    del polices[nom]

    nom_piece = o.get("nom_piece", "factur-x.xml")

    if not o.get("sans_piece_jointe"):
        piece = pikepdf.AttachedFileSpec(
            pdf, xml_bytes, filename=nom_piece,
            mime_type="text/xml",
            description="Factur-X invoice data",
        )
        if o.get("sans_afrelationship"):
            # pikepdf pose /Unspecified par défaut : il faut le retirer
            # explicitement, sinon le défaut n'est pas celui qu'on croit.
            if "/AFRelationship" in piece.obj:
                del piece.obj["/AFRelationship"]
        else:
            piece.obj["/AFRelationship"] = pikepdf.Name(
                o.get("afrelationship", "/Data"))
        pdf.attachments[nom_piece] = piece
        if not o.get("sans_af_racine"):
            pdf.Root["/AF"] = pdf.make_indirect([piece.obj])

    if not o.get("sans_xmp"):
        pdf.Root["/Metadata"] = pdf.make_stream(
            xmp_facturx(f, nom_piece, o).encode("utf-8"))

    if not o.get("sans_pdfa"):
        # Sans profil ICC embarqué, veraPDF rejette tout usage de DeviceGray.
        icc = None
        if CHEMIN_ICC and os.path.exists(CHEMIN_ICC):
            with open(CHEMIN_ICC, "rb") as fh:
                icc = pdf.make_stream(fh.read())
            icc.stream_dict["/N"] = 3
        oi = pikepdf.Dictionary(
            Type=pikepdf.Name("/OutputIntent"),
            S=pikepdf.Name("/GTS_PDFA1"),
            OutputConditionIdentifier=pikepdf.String("sRGB"),
            Info=pikepdf.String("sRGB IEC61966-2.1"),
        )
        if icc is not None:
            oi["/DestOutputProfile"] = icc
        pdf.Root["/OutputIntents"] = pdf.make_indirect([pdf.make_indirect(oi)])

    pdf.save(chemin)
    pdf.close()
    os.remove(tmp)


def xmp_facturx(f, nom_piece, o):
    """XMP avec déclaration du schéma d'extension.

    ISO 19005-3 clause 6.6.2.3 : toute propriété XMP hors schémas prédéfinis
    doit être déclarée dans un pdfaExtension:schemas. Sans ça, veraPDF rejette
    les quatre propriétés fx:* — c'est l'erreur PDF/A la plus fréquente des
    générateurs Factur-X maison.
    """
    profil = o.get("xmp_profil") or profil_court(f["profil"])
    version = o.get("xmp_version", "1.0")
    conformance = o.get("pdfa_conformance", "3")
    fx_ns = "urn:factur-x:pdfa:CrossIndustryDocument:invoice:1p0#"

    champs = [("DocumentType", "Text", "internal", "INVOICE"),
              ("DocumentFileName", "Text", "internal", nom_piece),
              ("Version", "Text", "internal", version),
              ("ConformanceLevel", "Text", "internal", profil)]

    proprietes = "\n".join(
        f"""       <rdf:li rdf:parseType="Resource">
        <pdfaProperty:name>{n}</pdfaProperty:name>
        <pdfaProperty:valueType>{vt}</pdfaProperty:valueType>
        <pdfaProperty:category>{cat}</pdfaProperty:category>
        <pdfaProperty:description>Factur-X {n}</pdfaProperty:description>
       </rdf:li>""" for n, vt, cat, _ in champs)

    valeurs = "\n".join(f"   <fx:{n}>{v}</fx:{n}>" for n, _, _, v in champs)

    extension = "" if o.get("sans_extension_xmp") else f"""
  <rdf:Description rdf:about=""
      xmlns:pdfaExtension="http://www.aiim.org/pdfa/ns/extension/"
      xmlns:pdfaSchema="http://www.aiim.org/pdfa/ns/schema#"
      xmlns:pdfaProperty="http://www.aiim.org/pdfa/ns/property#">
   <pdfaExtension:schemas>
    <rdf:Bag>
     <rdf:li rdf:parseType="Resource">
      <pdfaSchema:schema>Factur-X PDFA Extension Schema</pdfaSchema:schema>
      <pdfaSchema:namespaceURI>{fx_ns}</pdfaSchema:namespaceURI>
      <pdfaSchema:prefix>fx</pdfaSchema:prefix>
      <pdfaSchema:property>
       <rdf:Seq>
{proprietes}
       </rdf:Seq>
      </pdfaSchema:property>
     </rdf:li>
    </rdf:Bag>
   </pdfaExtension:schemas>
  </rdf:Description>"""

    return f"""<?xpacket begin="\ufeff" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
  <rdf:Description rdf:about="" xmlns:pdfaid="http://www.aiim.org/pdfa/ns/id/">
   <pdfaid:part>{conformance}</pdfaid:part>
   <pdfaid:conformance>B</pdfaid:conformance>
  </rdf:Description>{extension}
  <rdf:Description rdf:about="" xmlns:fx="{fx_ns}">
{valeurs}
  </rdf:Description>
 </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>"""


def profil_court(urn):
    if urn.endswith("basic"):
        return "BASIC"
    if urn == PROFIL_MINIMUM:
        return "MINIMUM"
    if urn == PROFIL_EN16931:
        return "EN 16931"
    return "BASIC"


# ---------------------------------------------------------------------------
# Catalogue des cas
# ---------------------------------------------------------------------------

# Références normatives vérifiées le 16/08/2026 contre les schematrons
# officiels (voir notes/references-normatives.md) :
#   EN 16931 — ConnectingEurope eInvoicing-EN16931, release validation-1.3.16,
#     EN16931-CII-validation-preprocessed.sch,
#     sha256 54e0dc6d06cd7f17d268bb9696ff56f58d386ee28961c9bbef0a56718c400c89
#   BR-FR — FNFE-MPE France_RFE, release v1.4.0.03 du 04/08/2026,
#     BR-FR-Flux2-Schematron-CII.sch (V1.4.0 du 30/06/2026),
#     sha256 d1172c6e89cc17fcdafcaaaf2ad57c2d1d1a576ad7694b5a6e5514a7cec0c4db
# Chaque cas indique l'assertion qui se déclenche réellement, avec son
# libellé officiel repris tel quel. Les cas qui ne déclenchent aucune
# assertion (conteneur PDF, tolérances d'implémentation) le disent.
VERIF_SCHEMATRONS = {
    "date": "16/08/2026",
    "en16931": "ConnectingEurope validation-1.3.16 (CII, preprocessed), "
               "sha256 54e0dc6d06cd7f17d268bb9696ff56f58d386ee28961c9bbef0"
               "a56718c400c89",
    "brfr": "FNFE-MPE France_RFE v1.4.0.03 du 04/08/2026, BR-FR-Flux2-"
            "Schematron-CII V1.4.0 du 30/06/2026, sha256 d1172c6e89cc17fcd"
            "afcaaaf2ad57c2d1d1a576ad7694b5a6e5514a7cec0c4db",
}


# Renumérotation des références, faite une seule fois, avant la première
# publication du corpus. Les préfixes BR-, FMT- et ID- pouvaient se lire
# comme des codes normatifs : `BR-001` n'a jamais désigné la règle EN 16931
# `BR-1`, et `FMT-` est par ailleurs pris côté moteur de diagnostic. Les
# références ci-dessous sont désormais stables.
RENOMMAGE = [
    ("BR-001", "CALC-001"), ("BR-002", "CALC-002"), ("BR-003", "CALC-003"),
    ("BR-004", "CALC-004"), ("BR-005", "CALC-005"), ("BR-006", "CALC-006"),
    ("FMT-001", "DATA-001"), ("FMT-002", "DATA-002"), ("FMT-003", "DATA-003"),
    ("FMT-004", "DATA-004"), ("FMT-005", "DATA-005"), ("FMT-006", "DATA-006"),
    ("ID-001", "IDENT-001"), ("ID-002", "IDENT-002"), ("ID-003", "IDENT-003"),
]

# Ce que chaque cas teste réellement — établi assertion par assertion contre
# les deux schematrons, pas déduit de la famille d'origine. C'est ce
# classement qui organise le README.
NATURES = {
    "non_norme": (
        "Non normé — aucune assertion ne se déclenche",
        "Le cœur du corpus. Ces documents passent la validation normative : "
        "aucune assertion EN 16931 ni BR-FR ne les rejette, et deux "
        "implémentations également conformes peuvent malgré tout les traiter "
        "différemment — l'une accepte, l'autre refuse, et le flux bloque sans "
        "qu'aucune des deux n'ait tort. C'est là que se logent les litiges "
        "d'interopérabilité que la norme ne tranche pas, et c'est ce qu'un "
        "corpus apporte qu'un validateur ne donne pas : la liste explicite "
        "de ce sur quoi il faut se mettre d'accord contractuellement."),
    "assertion": (
        "Déclenche une assertion officielle",
        "Un validateur conforme doit les rejeter, et nommer la règle. "
        "L'assertion exacte est indiquée, avec son libellé officiel repris "
        "tel quel dans la fiche du cas."),
    "amont": (
        "Échoue en amont du schematron",
        "Document mal formé ou hors schéma XSD : aucun schematron ne "
        "s'exécute. Le rejet doit être explicite sur la cause — un message "
        "de parseur brut n'est pas exploitable par l'émetteur."),
    "specification": (
        "Conteneur PDF/A-3 ou spécification Factur-X",
        "Le XML embarqué est valide ; c'est le conteneur ou la cohérence "
        "PDF/XML qui est en défaut. Aucune assertion de schematron ne porte "
        "sur ces points."),
    "temoin": (
        "Témoin",
        "La facture saine. Un validateur qui la rejette a un problème avant "
        "même de traiter les cas défectueux."),
}

# Ordre d'exposition dans le README : le groupe non normé d'abord, parce
# que c'est celui qui distingue ce corpus d'un simple validateur.
ORDRE_NATURES = ["temoin", "non_norme", "assertion", "amont", "specification"]

# ref -> (nature, assertions réellement déclenchées)
CLASSEMENT = {
    "OK-001": ("temoin", ""),
    "PDF-001": ("specification", ""),
    "PDF-002": ("specification", ""),
    "PDF-003": ("specification", ""),
    "PDF-004": ("non_norme", ""),
    "PDF-005": ("specification", ""),
    "PDF-006": ("specification", ""),
    "PDF-007": ("specification", ""),
    "PDF-008": ("specification", ""),
    "XML-001": ("amont", ""),
    "XML-002": ("amont", ""),
    "XML-003": ("amont", ""),
    "XML-004": ("assertion", "BR-01"),
    "CALC-001": ("assertion", "BR-CO-15, puis BR-CO-16"),
    "CALC-002": ("assertion", "BR-CO-10, puis BR-CO-13"),
    "CALC-003": ("assertion", "BR-CO-14, puis BR-CO-16"),
    "CALC-004": ("assertion", "BR-DEC-23, BR-FR-DEC-01_BT-131, BR-S-08"),
    "CALC-005": ("assertion", "BR-S-08 (deux fois)"),
    "CALC-006": ("assertion", "BR-E-10"),
    "IDENT-001": ("non_norme", ""),
    "IDENT-002": ("non_norme", ""),
    "IDENT-003": ("assertion", "BR-S-02"),
    "DATA-001": ("assertion", "BR-FR-03_BT-2, CII-DT-097"),
    "DATA-002": ("assertion", "BR-FR-03_BT-2"),
    "DATA-003": ("assertion", "BR-FR-CO-07_BT-9"),
    "DATA-004": ("assertion", "BR-05"),
    "DATA-005": ("amont", ""),
    "DATA-006": ("assertion", "BR-27, BR-FR-DEC-03_BT-146"),
    "PRF-001": ("non_norme", ""),
    "PRF-002": ("specification", ""),
    "RBT-001": ("non_norme", ""),
    "RBT-002": ("amont", ""),
}

# Cas qui ne testaient pas ce qu'ils annonçaient. Établi en confrontant
# chaque cas aux schematrons officiels — pas en relisant les intentions.
# (ref, ce qui était annoncé, ce que la vérification a établi)
CORRECTIONS = [
    ("IDENT-001", "ID-001 — « SIRET à 13 chiffres », violation de "
     "BR-CO-26, rejet attendu",
     "Le SIRET tronqué n'atteint jamais le XML : il n'existe que dans le "
     "visuel PDF. Le XML embarqué est celui du témoin à l'octet près "
     "(empreintes identiques). Aucune assertion ne se déclenche, un "
     "validateur conforme accepte. Le cas est conservé — il teste "
     "désormais ce qu'il testait en fait depuis le début : la cohérence "
     "entre le lisible et le structuré. Attendu corrigé en acceptation."),
    ("IDENT-002", "ID-002 — clé de TVA fausse, violation de BR-CO-09, "
     "rejet attendu",
     "BR-CO-09 ne vérifie que le préfixe pays ISO 3166-1, correct ici. "
     "Aucun schematron ne recalcule la clé française modulo 97. Un "
     "validateur normatif accepte ce document. Attendu corrigé en "
     "avertissement."),
    ("IDENT-003", "ID-003 — « vendeur sans aucun identifiant », violation "
     "de BR-CO-26",
     "L'identifiant légal (SIREN, schemeID 0002) reste présent dans le "
     "XML : BR-CO-26, qui exige au moins un identifiant parmi trois, "
     "tient. C'est BR-S-02 qui se déclenche — TVA facturée sans "
     "identifiant TVA du vendeur. Titre et règle corrigés."),
    ("CALC-005", "BR-005 — deux écritures du même taux, violation de "
     "BR-CO-17",
     "BR-CO-17 tient : chaque ventilation est arithmétiquement juste, et "
     "leur somme aussi (BR-CO-14 tient). C'est BR-S-08 qui se déclenche, "
     "deux fois — la comparaison des taux y est numérique, donc `20` et "
     "`20.00` sont le même taux, et chaque base déclarée ne vaut pas la "
     "somme des lignes à ce taux. Corrigé en deux temps : d'abord classé "
     "à tort « aucune assertion » sur lecture du schematron, puis rectifié "
     "en exécutant les validateurs."),
    ("DATA-006", "FMT-006 — « ligne à montant négatif », violation de la "
     "distinction TypeCode 380 / 381",
     "Un montant de ligne négatif (BT-131) est licite en EN 16931, y "
     "compris sur une facture 380 : c'est ainsi qu'on porte une remise en "
     "ligne. C'est le PRIX net négatif que BR-27 interdit. Rejeter tout "
     "montant négatif sur une 380 refuserait des factures valides."),
    ("PDF-008", "PDF-008 — entrée /AF absente, violation de PDF/A-3 §3.1",
     "PDF/A-3 n'exige pas le tableau /AF du catalogue. L'exigence vient "
     "de la spécification Factur-X, qui s'appuie sur les fichiers "
     "associés d'ISO 32000-2. Norme source corrigée ; le défaut et le "
     "comportement attendu sont inchangés."),
    ("DATA-003", "FMT-003 — échéance antérieure à l'émission, « aucune "
     "règle ne l'interdit », avertissement attendu",
     "Le schematron français l'interdit explicitement : BR-FR-CO-07_BT-9 "
     "exige une échéance postérieure ou égale à la date de facture, sauf "
     "acompte (386, 500, 503) ou cadre B2/S2/M2. L'affirmation « aucune "
     "assertion » ne valait que pour le schematron européen. Attendu "
     "corrigé en rejet."),
    ("XML-002", "XML-002 — namespace erroné, « aucun contexte de "
     "schematron ne correspond plus »",
     "Faux : les éléments `ram:` continuent de correspondre, seule la "
     "racine `rsm:` ne correspond plus. Exécuter le schematron sur ce "
     "document produit trois erreurs qui désignent autre chose "
     "(BR-CO-18, BR-S-08, CII-DT-033) — ce qui rend le cas plus "
     "instructif, pas moins : il montre ce que coûte de sauter la "
     "validation XSD."),
]


@dataclass
class Cas:
    ref: str
    titre: str
    categorie: str
    regle: str
    attendu: str                     # "rejet" | "acceptation" | "avertissement"
    description: str
    piege: str = ""                  # pourquoi une implémentation le rate
    source: str = ""                 # d'où vient l'exigence
    libelle_officiel: str = ""       # texte du schematron, jamais reformulé
    muter_facture: Optional[Callable] = None
    muter_xml: Optional[Callable] = None
    options_pdf: dict = field(default_factory=dict)
    approximatif: bool = False


def catalogue():
    C = []

    # --- témoin ---
    C.append(Cas(
        "OK-001", "Facture conforme (témoin)", "témoin",
        "EN 16931 — profil BASIC", "acceptation",
        "Facture saine. Sert de référence : un validateur qui la rejette a un "
        "problème avant même de traiter les cas défectueux.",
        piege="Un validateur trop strict sur des champs optionnels rejette "
              "ce témoin. C'est le premier test à passer.",
        source="EN 16931 · BR-FR / FNFE-MPE",
    ))

    # --- structure PDF ---
    # Aucune assertion des schematrons EN 16931 / BR-FR ne porte sur le
    # conteneur : ces cas relèvent de la spécification Factur-X et des
    # normes ISO du PDF, et le disent explicitement.
    C.append(Cas(
        "PDF-001", "Aucun XML embarqué", "structure PDF",
        "Factur-X 1.0.07 — XML embarqué obligatoire (hors schematron)",
        "rejet",
        "PDF visuellement identique à une facture Factur-X, mais sans fichier "
        "embarqué. Aucune assertion EN 16931 / BR-FR ne se déclenche : le "
        "contrôle est au niveau du conteneur PDF, avant toute validation XML.",
        piege="Certaines implémentations renvoient une erreur générique "
              "indistinguable d'un fichier corrompu.",
        source="Factur-X 1.0.07 (FNFE-MPE / FeRD)",
        options_pdf={"sans_piece_jointe": True},
    ))
    C.append(Cas(
        "PDF-002", "Nom de pièce jointe non normalisé", "structure PDF",
        "Factur-X 1.0.07 — nom de fichier factur-x.xml (hors schematron)",
        "rejet",
        "Le XML est embarqué sous le nom `facture.xml` au lieu de "
        "`factur-x.xml`. Contrôle au niveau du conteneur : aucune assertion "
        "de schematron ne se déclenche.",
        piege="Une implémentation qui scanne toutes les pièces jointes "
              "l'accepte, une autre qui cherche le nom exact ne le trouve pas. "
              "Les deux comportements existent en production.",
        source="Factur-X 1.0.07 (FNFE-MPE / FeRD)",
        options_pdf={"nom_piece": "facture.xml"},
    ))
    C.append(Cas(
        "PDF-003", "AFRelationship absent", "structure PDF",
        "ISO 19005-3 (PDF/A-3) — clé AFRelationship obligatoire", "rejet",
        "La pièce jointe existe mais ne déclare pas sa relation au document. "
        "Contrôle PDF/A-3, hors schematron.",
        piege="L'extraction fonctionne quand même ; seule une validation "
              "PDF/A-3 stricte le détecte.",
        source="ISO 19005-3",
        options_pdf={"sans_afrelationship": True},
    ))
    C.append(Cas(
        "PDF-004", "AFRelationship incorrect (/Source)", "structure PDF",
        "Factur-X 1.0.07 — AFRelationship attendu /Data ; tolérance "
        "d'implémentation", "avertissement",
        "Relation déclarée `/Source` au lieu de `/Data`. Comportement non "
        "normé au sens des schematrons ; la valeur attendue a varié selon "
        "les versions de la spécification (ZUGFeRD 2.0 utilisait "
        "/Alternative), d'où des divergences d'implémentation.",
        piege="Cas fréquent en production. Toléré par la plupart des lecteurs, "
              "signalé par les validateurs stricts. À traiter en "
              "avertissement, pas en rejet.",
        source="Factur-X 1.0.07 (FNFE-MPE / FeRD)",
        options_pdf={"afrelationship": "/Source"},
    ))
    C.append(Cas(
        "PDF-005", "Métadonnées XMP Factur-X absentes", "structure PDF",
        "Factur-X 1.0.07 — extension XMP obligatoire (hors schematron)",
        "rejet",
        "Aucune métadonnée XMP ne déclare le profil ni le nom du fichier. "
        "Contrôle au niveau du conteneur PDF.",
        piege="Le XML reste extractible : une implémentation qui ne lit que "
              "la pièce jointe ne verra jamais le problème.",
        source="Factur-X 1.0.07 (FNFE-MPE / FeRD)",
        options_pdf={"sans_xmp": True},
    ))
    C.append(Cas(
        "PDF-006", "XMP déclare un profil différent du XML", "structure PDF",
        "Factur-X 1.0.07 — cohérence XMP / GuidelineID (hors schematron)",
        "rejet",
        "Le XMP annonce MINIMUM, le XML déclare BASIC. Seul un contrôle "
        "croisé des deux sources le voit ; aucune assertion de schematron "
        "ne porte sur le XMP.",
        piege="Défaut invisible sans contrôle croisé des deux sources. "
              "Très rarement implémenté.",
        source="Factur-X 1.0.07 (FNFE-MPE / FeRD)",
        options_pdf={"xmp_profil": "MINIMUM"},
    ))
    C.append(Cas(
        "PDF-007", "Pas de PDF/A (OutputIntent absent)", "structure PDF",
        "ISO 19005-3 — conformité PDF/A-3", "rejet",
        "PDF ordinaire portant un XML Factur-X. Hors schematron : le XML "
        "embarqué reste, lui, parfaitement valide.",
        piege="Techniquement exploitable, réglementairement non conforme — "
              "c'est le défaut le plus fréquent des générateurs maison.",
        source="ISO 19005-3",
        options_pdf={"sans_pdfa": True}, approximatif=True,
    ))
    C.append(Cas(
        "PDF-008", "Entrée /AF absente à la racine", "structure PDF",
        "Factur-X 1.0.07 — tableau /AF du catalogue (ISO 32000-2)", "rejet",
        "La pièce jointe est dans /Names mais pas référencée dans /AF. "
        "L'exigence du tableau /AF vient de la spécification Factur-X, qui "
        "s'appuie sur les fichiers associés d'ISO 32000-2 — pas de "
        "PDF/A-3, qui ne le requiert pas.",
        piege="Extraction possible, conformité Factur-X fausse. Classique des "
              "bibliothèques qui attachent sans mettre à jour le catalogue.",
        source="Factur-X 1.0.07 (FNFE-MPE / FeRD) · ISO 32000-2",
        options_pdf={"sans_af_racine": True},
    ))

    # --- structure XML ---
    def xml_tronque(x):
        return x[: int(len(x) * 0.7)]

    C.append(Cas(
        "XML-001", "XML tronqué", "structure XML",
        "W3C XML 1.0 — document bien formé (en amont de tout schematron)",
        "rejet",
        "Le fichier embarqué s'arrête au milieu d'une balise. Aucun "
        "schematron ne s'exécute sur un document mal formé : l'erreur est "
        "au niveau du parseur.",
        piege="Doit produire une erreur de parsing explicite, pas un plantage "
              "ni un rejet silencieux.",
        source="W3C XML 1.0",
        muter_xml=xml_tronque,
    ))
    C.append(Cas(
        "XML-002", "Espace de noms rsm erroné", "structure XML",
        "UN/CEFACT CII — espace de noms :100 (validation XSD, en amont du "
        "schematron)", "rejet",
        "Le namespace CrossIndustryInvoice pointe vers une version 90 au "
        "lieu de 100 : le document est hors schéma et la validation XSD "
        "échoue. Le document reste bien formé, et exécuter le schematron "
        "malgré tout — mesuré — produit des erreurs qui désignent autre "
        "chose : BR-CO-18 « aucune ventilation de TVA », BR-S-08, "
        "CII-DT-033. Les éléments `ram:` continuent en effet de "
        "correspondre, seule la racine `rsm:` ne correspond plus.",
        piege="Un parseur permissif ignore le namespace et traite le "
              "document comme valide. Pire : sauter la validation XSD pour "
              "n'exécuter que le schematron produit trois erreurs qui "
              "pointent toutes à côté, et l'émetteur corrige des montants "
              "qui n'ont rien à se reprocher.",
        source="UN/CEFACT CII (XSD)",
        muter_xml=lambda x: x.replace("CrossIndustryInvoice:100",
                                      "CrossIndustryInvoice:90"),
    ))
    C.append(Cas(
        "XML-003", "Déclaration d'encodage mensongère", "structure XML",
        "W3C XML 1.0 §4.3.3 — déclaration d'encodage", "rejet",
        "En-tête `encoding=\"UTF-8\"` sur un contenu encodé en ISO-8859-1. "
        "En amont de tout schematron.",
        piege="Les accents deviennent illisibles sans erreur. Le nom de "
              "l'acheteur est corrompu en silence — cas typique de défaut "
              "qui passe la validation et casse la comptabilité.",
        source="W3C XML 1.0",
        muter_xml=lambda x: x,   # traité au moment de l'écriture
    ))
    C.append(Cas(
        "XML-004", "GuidelineID absent", "structure XML",
        "EN 16931 — BR-01", "rejet",
        "Identifiant de profil vide : impossible de savoir quelles règles "
        "appliquer. L'assertion vérifie que l'élément, une fois normalisé, "
        "n'est pas vide — un élément présent mais vide déclenche bien la "
        "règle.",
        piege="Certaines implémentations supposent BASIC par défaut au lieu "
              "de rejeter.",
        source="EN 16931",
        libelle_officiel="An Invoice shall have a Specification identifier "
                         "(BT-24).",
        muter_xml=lambda x: x.replace(
            f"<ram:ID>{PROFIL_BASIC}</ram:ID>", "<ram:ID></ram:ID>"),
    ))

    # --- règles de gestion ---
    def total_faux(f):
        f["_forcer_totaux"] = {"total_ttc": 3000.00}
        return f

    C.append(Cas(
        "CALC-001", "Total TTC ≠ HT + TVA", "calcul et ventilation",
        "EN 16931 — BR-CO-15", "rejet",
        "Le total TTC déclaré ne correspond pas à la somme du HT et de la "
        "TVA. Le net à payer n'ayant pas été recalé, BR-CO-16 (net à payer "
        "= TTC − payé + arrondi) se déclenche aussi.",
        piege="Le contrôle le plus élémentaire, et pourtant celui que les "
              "générateurs maison omettent le plus souvent.",
        source="EN 16931",
        libelle_officiel="Invoice total amount with VAT (BT-112) = Invoice "
                         "total amount without VAT (BT-109) + Invoice total "
                         "VAT amount (BT-110).",
        muter_facture=total_faux,
    ))

    def somme_lignes_fausse(f):
        f["_forcer_totaux"] = {"lignes_ht": 2600.00}
        return f

    C.append(Cas(
        "CALC-002", "Somme des lignes ≠ total des lignes",
        "calcul et ventilation",
        "EN 16931 — BR-CO-10", "rejet",
        "Le champ LineTotalAmount ne correspond pas à la somme des montants "
        "de ligne. Le total HT restant calé sur les lignes réelles, "
        "BR-CO-13 (total HT = somme des lignes − remises + charges) se "
        "déclenche aussi.",
        piege="Souvent causé par un arrondi appliqué au total plutôt que "
              "ligne par ligne.",
        source="EN 16931",
        libelle_officiel="Sum of Invoice line net amount (BT-106) = Σ "
                         "Invoice line net amount (BT-131).",
        muter_facture=somme_lignes_fausse,
    ))

    def tva_incoherente(f):
        f["_forcer_totaux"] = {"total_tva": 500.00, "total_ttc": 3035.00}
        return f

    C.append(Cas(
        "CALC-003", "Ventilation TVA ≠ total TVA", "calcul et ventilation",
        "EN 16931 — BR-CO-14", "rejet",
        "Le total de TVA ne correspond pas à la somme des montants ventilés "
        "par taux. Le net à payer n'ayant pas été recalé sur le TTC forcé, "
        "BR-CO-16 se déclenche aussi.",
        piege="Passe inaperçu quand un seul taux est présent et que le "
              "contrôle porte sur le total global.",
        source="EN 16931",
        libelle_officiel="Invoice total VAT amount (BT-110) = Σ VAT "
                         "category tax amount (BT-117).",
        muter_facture=tva_incoherente,
    ))

    def arrondi_limite(f):
        f["lignes"] = [{"id": "1", "designation": "Prestation au 1/2 centime",
                        "quantite": "3.00", "unite": "C62",
                        "prix_unitaire": "33.335", "montant_ht": "100.005",
                        "taux_tva": "20.00", "categorie_tva": "S"}]
        return f

    C.append(Cas(
        "CALC-004", "Arrondi au demi-centime", "calcul et ventilation",
        "EN 16931 — BR-DEC-23", "rejet",
        "Montant de ligne à trois décimales, à la frontière de l'arrondi. "
        "Se déclenchent aussi, mesuré : BR-FR-DEC-01_BT-131 (même exigence "
        "de deux décimales côté français) et BR-S-08 (la base de TVA "
        "déclarée ne retombe pas sur la somme des lignes, précisément à "
        "cause du demi-centime). BR-CO-10, en revanche, tient : l'arrondi "
        "de la somme des lignes coïncide avec le total déclaré.",
        piege="Selon la stratégie d'arrondi (banquier ou demi-supérieur), "
              "deux implémentations calculent un TTC différent d'un centime "
              "et se rejettent mutuellement. Cause n°1 des litiges de "
              "rapprochement.",
        source="EN 16931 · BR-FR / FNFE-MPE",
        libelle_officiel="The allowed maximum number of decimals for the "
                         "Invoice line net amount (BT-131) is 2.",
        muter_facture=arrondi_limite,
    ))

    def taux_formats(f):
        f["lignes"][1]["taux_tva"] = "20"
        return f

    C.append(Cas(
        "CALC-005", "Même taux, deux écritures (20 et 20.00)",
        "calcul et ventilation",
        "EN 16931 — BR-S-08", "rejet",
        "Deux lignes au même taux réel, écrit `20.00` puis `20`, produisant "
        "deux ventilations TVA distinctes pour un même couple "
        "catégorie/taux. BR-CO-17 tient — chaque ventilation est "
        "arithmétiquement juste — et BR-CO-14 aussi. C'est BR-S-08 qui se "
        "déclenche, deux fois : la comparaison des taux y est numérique, "
        "`20` et `20.00` sont donc le même taux, et la base déclarée par "
        "chaque ventilation (2 400,00 puis 135,00) ne vaut pas la somme "
        "des lignes à ce taux (2 535,00).",
        piege="Un regroupement par chaîne de caractères crée deux "
              "ventilations distinctes au lieu d'une. Le validateur ne "
              "nomme pas le vrai problème : il signale des bases de TVA "
              "fausses, alors que la cause est un regroupement raté. "
              "Chercher l'erreur dans les montants fait perdre des heures.",
        source="EN 16931",
        libelle_officiel="For each different value of VAT category rate "
                         "(BT-119) where the VAT category code (BT-118) is "
                         "\"Standard rated\", the VAT category taxable "
                         "amount (BT-116) in a VAT breakdown (BG-23) shall "
                         "equal the sum of Invoice line net amounts "
                         "(BT-131) plus the sum of document level charge "
                         "amounts (BT-99) minus the sum of document level "
                         "allowance amounts (BT-92) where the VAT category "
                         "code (BT-151, BT-102, BT-95) is \"Standard "
                         "rated\" and the VAT rate (BT-152, BT-103, BT-96) "
                         "equals the VAT category rate (BT-119).",
        muter_facture=taux_formats,
    ))

    def exoneration_sans_motif(f):
        for l in f["lignes"]:
            l["categorie_tva"] = "E"
            l["taux_tva"] = "0.00"
        return f

    C.append(Cas(
        "CALC-006", "Exonération sans motif déclaré",
        "calcul et ventilation",
        "EN 16931 — BR-E-10", "rejet",
        "Catégorie TVA « E » sans code ni texte d'exonération.",
        piege="Cas très fréquent chez les auto-entrepreneurs en franchise de "
              "TVA. Souvent accepté à tort.",
        source="EN 16931",
        libelle_officiel="A VAT Breakdown (BG-23) with VAT Category code "
                         "(BT-118) \"Exempt from VAT\" shall have a VAT "
                         "exemption reason code (BT-121) or a VAT exemption "
                         "reason text (BT-120).",
        muter_facture=exoneration_sans_motif,
    ))

    # --- identifiants ---
    def siret_court(f):
        f["vendeur"]["siret"] = "3928091370002"
        return f

    C.append(Cas(
        "IDENT-001", "SIRET à 13 chiffres dans le visuel PDF", "identifiants",
        "comportement non normé — incohérence entre le visuel PDF et le "
        "XML (le XML reste conforme)", "acceptation",
        "Zéro de tête perdu, typiquement par un passage en tableur — mais "
        "uniquement dans le SIRET affiché sur le visuel PDF. Le XML "
        "embarqué (SIREN schemeID 0002, adresse de routage, TVA) est "
        "identique au témoin, à l'octet près : aucune assertion ne se "
        "déclenche, un validateur conforme accepte ce document. Le cas "
        "teste le croisement entre le lisible et le structuré, que "
        "presque aucune implémentation ne fait.",
        piege="Le défaut est invisible pour tout contrôle du XML. Seul un "
              "rapprochement du visuel et des données structurées le voit — "
              "et c'est pourtant le visuel que le comptable lit.",
        source="comportement non normé",
        muter_facture=siret_court,
    ))

    def tva_invalide(f):
        f["vendeur"]["tva"] = "FR00392809137"
        return f

    C.append(Cas(
        "IDENT-002", "Clé de TVA intracommunautaire fausse", "identifiants",
        "aucune assertion — contrôle métier (clé française), hors "
        "schematron", "avertissement",
        "Numéro de TVA au bon format mais dont la clé de contrôle est "
        "fausse. BR-CO-09, la seule règle officielle sur ce champ, ne "
        "vérifie que le préfixe pays ISO 3166-1 — correct ici. Aucun "
        "schematron ne recalcule la clé française (modulo 97) : un "
        "validateur normatif accepte ce document. Une implémentation "
        "soignée recalcule la clé et signale.",
        piege="Le contrôle de format passe, le contrôle de clé n'est presque "
              "jamais implémenté — et n'est exigé par aucune norme.",
        source="comportement non normé",
        muter_facture=tva_invalide,
    ))

    def sans_id_vendeur(f):
        f["vendeur"]["siret"] = None
        f["vendeur"]["tva"] = None
        return f

    C.append(Cas(
        "IDENT-003", "Vendeur sans identifiant TVA (lignes taxées)",
        "identifiants",
        "EN 16931 — BR-S-02", "rejet",
        "L'identifiant TVA du vendeur est retiré alors que les lignes sont "
        "en catégorie « Standard rated ». L'identifiant légal (SIREN, "
        "schemeID 0002) reste présent dans le XML : BR-CO-26, qui exige au "
        "moins un identifiant parmi trois, tient. C'est BR-S-02 qui se "
        "déclenche — TVA facturée sans identifiant TVA du vendeur.",
        piege="Une implémentation qui ne teste que « au moins un "
              "identifiant » (BR-CO-26) accepte ce document à tort : la "
              "règle applicable dépend de la catégorie de TVA des lignes.",
        source="EN 16931",
        libelle_officiel="An Invoice that contains an Invoice line (BG-25) "
                         "where the Invoiced item VAT category code "
                         "(BT-151) is \"Standard rated\" shall contain the "
                         "Seller VAT Identifier (BT-31), the Seller tax "
                         "registration identifier (BT-32) and/or the "
                         "Seller tax representative VAT identifier "
                         "(BT-63).",
        muter_facture=sans_id_vendeur,
    ))

    # --- formats ---
    def date_format_court(f):
        f["date_emission"] = "2026-08-15"
        return f

    C.append(Cas(
        "DATA-001", "Date en ISO au lieu du format 102", "formats de valeurs",
        "BR-FR / FNFE-MPE — BR-FR-03_BT-2", "rejet",
        "Date écrite `2026-08-15` alors que l'attribut annonce le format "
        "102. BR-03 ne se déclenche pas : il vérifie seulement que "
        "l'élément est présent et non vide. Se déclenchent, mesuré : "
        "BR-FR-03_BT-2 (format AAAAMMJJ, schematron français) et "
        "CII-DT-097, la règle de syntaxe CII qui impose AAAAMMJJ quand "
        "l'attribut `format` vaut 102.",
        piege="Un parseur tolérant lit la date correctement et masque une "
              "non-conformité qui cassera chez le destinataire suivant.",
        source="BR-FR / FNFE-MPE",
        libelle_officiel="La date d'émission (udt:DateTimeString) doit "
                         "contenir une année comprise entre 2000 et 2099, "
                         "au format AAAAMMJJ.",
        muter_facture=date_format_court,
    ))

    def date_impossible(f):
        f["date_emission"] = "20260230"
        return f

    C.append(Cas(
        "DATA-002", "Date inexistante (30 février)", "formats de valeurs",
        "BR-FR / FNFE-MPE — BR-FR-03_BT-2", "rejet",
        "Date au bon format AAAAMMJJ mais qui n'existe pas au calendrier. "
        "Côté EN 16931, rien ne se déclenche — BR-03 ne vérifie que la "
        "présence. La fonction de contrôle du schematron français valide "
        "le calendrier réel, années bissextiles comprises : c'est elle qui "
        "attrape le 30 février.",
        piege="Le contrôle de format passe. Seule une conversion réelle en "
              "date détecte le problème — le schematron français la fait, "
              "pas l'européen.",
        source="BR-FR / FNFE-MPE",
        libelle_officiel="La date d'émission (udt:DateTimeString) doit "
                         "contenir une année comprise entre 2000 et 2099, "
                         "au format AAAAMMJJ.",
        muter_facture=date_impossible,
    ))

    def echeance_anterieure(f):
        f["echeance"] = "20260701"
        return f

    C.append(Cas(
        "DATA-003", "Échéance antérieure à l'émission", "formats de valeurs",
        "BR-FR / FNFE-MPE — BR-FR-CO-07_BT-9", "rejet",
        "Date d'échéance avant la date de facture. Côté EN 16931, rien ne "
        "se déclenche : aucune assertion européenne ne compare ces deux "
        "dates. Le profil français, lui, l'interdit — sauf facture "
        "d'acompte (386, 500, 503) ou cadre de facturation B2, S2, M2, "
        "où l'échéance antérieure est légitime.",
        piege="Une implémentation qui ne charge que le schematron européen "
              "accepte ce document. C'est le cas d'école de l'écart entre "
              "conformité EN 16931 et conformité au profil français : les "
              "deux jeux de règles doivent tourner.",
        source="BR-FR / FNFE-MPE",
        libelle_officiel="La date d’échéance (BT-9), si présente, doit "
                         "être postérieure ou égale à la date de facture "
                         "(BT-2), sauf si la facture est de type acompte "
                         "(386, 500, 503) ou si le cadre de facturation "
                         "(BT-23) est B2, S2 ou M2.",
        muter_facture=echeance_anterieure,
    ))

    def sans_devise(f):
        f["devise"] = None
        return f

    C.append(Cas(
        "DATA-004", "Devise absente", "formats de valeurs",
        "EN 16931 — BR-05", "rejet",
        "Aucun code devise déclaré au niveau document.",
        piege="Une implémentation qui suppose EUR par défaut accepte le "
              "document et fausse tout traitement multidevise ultérieur.",
        source="EN 16931",
        libelle_officiel="An Invoice shall have an Invoice currency code "
                         "(BT-5).",
        muter_facture=sans_devise,
    ))

    def separateur_virgule(f):
        f["lignes"][0]["montant_ht"] = "2400,00"
        return f

    C.append(Cas(
        "DATA-005", "Séparateur décimal virgule", "formats de valeurs",
        "XSD UN/CEFACT CII — xs:decimal, point décimal (en amont du "
        "schematron)", "rejet",
        "Montant écrit `2400,00`. La validation XSD échoue avant le "
        "schematron — la double validation XSD + schematron est celle "
        "prévue par XP Z12-012.",
        piege="Le défaut le plus courant des générateurs développés en "
              "France. Un parseur qui remplace la virgule en silence masque "
              "un bug de génération.",
        source="UN/CEFACT CII (XSD)",
        muter_facture=separateur_virgule,
    ))

    def montant_negatif(f):
        f["lignes"][1]["montant_ht"] = "-135.00"
        f["lignes"][1]["prix_unitaire"] = "-45.00"
        return f

    C.append(Cas(
        "DATA-006", "Prix net négatif sur une ligne", "formats de valeurs",
        "EN 16931 — BR-27", "rejet",
        "Prix unitaire net et montant de ligne négatifs. C'est le PRIX "
        "négatif qui est interdit (BR-27) : un montant de ligne négatif "
        "(BT-131) est licite en EN 16931, même sur une facture de type "
        "380 — c'est ainsi qu'on porte une remise en ligne. Le profil "
        "français ajoute BR-FR-DEC-03_BT-146, qui exige lui aussi un prix "
        "strictement positif hors contrats bi-directionnels.",
        piege="L'intuition « négatif = avoir (381) » est fausse au niveau "
              "de la ligne : rejeter tout montant négatif sur une 380 "
              "refuse des factures valides ; accepter un prix négatif "
              "viole la norme. La règle est sur le prix, pas sur le "
              "montant.",
        source="EN 16931",
        libelle_officiel="The Item net price (BT-146) shall NOT be "
                         "negative.",
        muter_facture=montant_negatif,
    ))

    # --- profils ---
    def profil_minimum_contenu_basic(f):
        f["profil"] = PROFIL_MINIMUM
        return f

    C.append(Cas(
        "PRF-001", "Profil MINIMUM avec contenu BASIC", "profils",
        "Factur-X 1.0.07 — cohérence profil / contenu (hors schematron ; "
        "divergence d'implémentation)", "avertissement",
        "Le document déclare MINIMUM mais contient des lignes de détail, "
        "absentes de ce profil. Aucune assertion EN 16931 / BR-FR ne "
        "compare le contenu au profil déclaré : le contrôle relève du "
        "schéma du profil Factur-X.",
        piege="Techniquement plus riche que déclaré. Faut-il rejeter ou "
              "accepter ? Les implémentations divergent, et c'est exactement "
              "le genre d'écart qui bloque un flux en production.",
        source="Factur-X 1.0.07 (FNFE-MPE / FeRD)",
        muter_facture=profil_minimum_contenu_basic,
    ))

    def profil_inconnu(f):
        f["profil"] = "urn:factur-x.eu:2p0:ultimate"
        return f

    C.append(Cas(
        "PRF-002", "Profil inexistant", "profils",
        "Factur-X 1.0.07 / XP Z12-012 — liste fermée des profils (hors "
        "schematron EN / BR-FR)", "rejet",
        "Identifiant de profil qui ne correspond à aucune spécification. "
        "Ni le schematron EN 16931 ni le BR-FR ne vérifient la valeur de "
        "l'URN (BR-01 exige seulement qu'il soit non vide) : c'est le "
        "validateur qui, ne pouvant pas sélectionner de jeu de règles, "
        "doit rejeter en nommant le profil reçu.",
        piege="Le rejet doit nommer le profil reçu. Une erreur générique "
              "oblige l'émetteur à deviner.",
        source="Factur-X 1.0.07 (FNFE-MPE / FeRD) · XP Z12-012",
        muter_facture=profil_inconnu,
    ))

    # --- robustesse ---
    def designation_tres_longue(f):
        f["lignes"][0]["designation"] = "Prestation " + "très " * 200 + "longue"
        return f

    C.append(Cas(
        "RBT-001", "Désignation de 1 000 caractères", "robustesse",
        "comportement non normé — aucune limite de longueur dans les "
        "schematrons", "acceptation",
        "Libellé de ligne anormalement long. Aucune assertion ne borne la "
        "longueur d'un libellé.",
        piege="Doit être accepté. Une troncature silencieuse en base est un "
              "défaut grave et invisible.",
        source="comportement non normé",
        muter_facture=designation_tres_longue,
    ))

    def caracteres_speciaux(f):
        f["acheteur"]["nom"] = "Mairie d'Ax-les-Thermes — service « achats »"
        f["lignes"][0]["designation"] = "Maintenance CVC <urgent> & réglage"
        return f

    C.append(Cas(
        "RBT-002", "Caractères spéciaux et entités XML", "robustesse",
        "W3C XML 1.0 §2.4 — échappement (en amont de tout schematron)",
        "rejet",
        "Chevrons et esperluette non échappés dans les libellés : le "
        "document est mal formé, aucun schematron ne s'exécute.",
        piege="Un générateur qui concatène des chaînes sans échapper produit "
              "un XML mal formé. Le test vérifie que le validateur le dit "
              "clairement au lieu de planter.",
        source="W3C XML 1.0",
        muter_facture=caracteres_speciaux,
    ))

    return C


# ---------------------------------------------------------------------------
# Génération
# ---------------------------------------------------------------------------

def generer_cas(cas, racine):
    f = facture_reference()
    if cas.muter_facture:
        f = cas.muter_facture(copy.deepcopy(f))

    t = totaux(f)
    if "_forcer_totaux" in f:
        t.update(f.pop("_forcer_totaux"))

    xml = construire_xml(f, t)
    if cas.muter_xml:
        xml = cas.muter_xml(xml)

    dossier = os.path.join(racine, cas.ref)
    os.makedirs(dossier, exist_ok=True)

    if cas.ref == "XML-003":
        octets = xml.encode("iso-8859-1", errors="replace")
    else:
        octets = xml.encode("utf-8")

    with open(os.path.join(dossier, "factur-x.xml"), "wb") as fh:
        fh.write(octets)

    chemin_pdf = os.path.join(dossier, "facture.pdf")
    construire_pdf(octets, f, chemin_pdf, cas.options_pdf)

    with open(os.path.join(dossier, "README.md"), "w", encoding="utf-8") as fh:
        fh.write(fiche_cas(cas, octets, chemin_pdf))

    nature, assertions = CLASSEMENT[cas.ref]
    return {
        "ref": cas.ref, "titre": cas.titre, "categorie": cas.categorie,
        "regle": cas.regle, "attendu": cas.attendu,
        "nature": nature, "assertions_declenchees": assertions,
        "source": cas.source, "libelle_officiel": cas.libelle_officiel,
        "description": cas.description, "piege": cas.piege,
        "pdfa_approximatif": cas.approximatif,
        "sha256_xml": hashlib.sha256(octets).hexdigest()[:16],
        "taille_pdf": os.path.getsize(chemin_pdf),
    }


def fiche_cas(cas, octets, chemin_pdf):
    avert = ("\n> Ce cas porte sur la conformité PDF/A-3, produite ici de "
             "façon approchée (profil ICC non embarqué). Le résultat est "
             "indicatif.\n" if cas.approximatif else "")
    officiel = (f"| Libellé officiel | {cas.libelle_officiel} |\n"
                if cas.libelle_officiel else "")
    nature, assertions = CLASSEMENT[cas.ref]
    decl = (f"| Assertions déclenchées | {assertions} |\n"
            if assertions else "")
    return f"""# {cas.ref} — {cas.titre}

| | |
|---|---|
| Catégorie | {cas.categorie} |
| Ce que le cas teste | {NATURES[nature][0]} |
| Règle | {cas.regle} |
| Source de l'exigence | {cas.source or "—"} |
{decl}{officiel}| Comportement attendu | **{cas.attendu}** |

Références vérifiées le {VERIF_SCHEMATRONS['date']} contre les schematrons
officiels (versions en tête du README du corpus). La référence du cas
({cas.ref}) est un identifiant du corpus, pas un code de norme.

## Le défaut

{cas.description}

## Pourquoi une implémentation le rate

{cas.piege or "—"}
{avert}
## Fichiers

- `facture.pdf` — le document complet
- `factur-x.xml` — le XML seul, pour tester le validateur sans passer par
  l'extraction

## Ce qu'on attend d'un rejet

Un rejet doit nommer la règle violée et le champ concerné. Un message du type
« ce fichier n'a pas pu être traité » n'est pas exploitable par l'émetteur :
c'est précisément le défaut que ce corpus cherche à mesurer.

---
Corpus de test Factur-X. Documents fictifs, sans valeur légale.
"""


def commande_generate(sortie):
    if os.path.exists(sortie):
        shutil.rmtree(sortie)
    os.makedirs(sortie)

    cas_list = catalogue()
    resultats = []
    for c in cas_list:
        try:
            resultats.append(generer_cas(c, sortie))
            print(f"  {c.ref:<9} {c.titre}")
        except Exception as e:
            print(f"  {c.ref:<9} ÉCHEC — {e}", file=sys.stderr)

    with open(os.path.join(sortie, "manifeste.json"), "w",
              encoding="utf-8") as fh:
        json.dump({"genere_le": date.today().isoformat(),
                   "references_normatives": VERIF_SCHEMATRONS,
                   "nombre_de_cas": len(resultats),
                   "cas": resultats}, fh, ensure_ascii=False, indent=2)

    with open(os.path.join(sortie, "README.md"), "w", encoding="utf-8") as fh:
        fh.write(readme_global(resultats))

    print(f"\n{len(resultats)} cas générés dans {sortie}/")
    return resultats


def readme_global(resultats):
    par_nature = {}
    for r in resultats:
        par_nature.setdefault(r["nature"], []).append(r)

    L = ["# Corpus de cas limites Factur-X", "",
         f"{len(resultats)} factures Factur-X portant chacune un défaut "
         "précis, avec l'assertion réellement violée et le comportement "
         "attendu.", "",
         "## À quoi ça sert", "",
         "Tester une implémentation Factur-X sur ce qu'elle laisse passer et "
         "sur ce qu'elle rejette à tort. La question n'est pas seulement "
         "« accepte-t-elle une facture valide », mais « quand elle refuse, "
         "dit-elle pourquoi ». Un rejet qui ne nomme pas la règle violée "
         "oblige l'émetteur à deviner, et c'est ce qui remplit les files de "
         "support.", "",
         "## Usage", "",
         "Ces fichiers sont destinés à tester votre propre implémentation, ou "
         "une implémentation publique et librement accessible. Ne les "
         "soumettez pas au système de production d'un tiers sans y avoir été "
         "invité.", "",
         "## Références normatives", "",
         "Les 32 documents ont été passés aux validateurs officiels, et le "
         "classement ci-dessous est celui des assertions réellement "
         "obtenues — pas d'une lecture des règles. Quand une assertion se "
         "déclenche, son libellé officiel est repris tel quel. Vérifié le "
         f"{VERIF_SCHEMATRONS['date']} contre :", "",
         f"- EN 16931 : {VERIF_SCHEMATRONS['en16931']}",
         f"- BR-FR : {VERIF_SCHEMATRONS['brfr']}", "",
         "Exécution via les XSLT compilés publiés dans ces mêmes releases, "
         "sous Saxon-HE 13 (XSLT 2.0). Le témoin `OK-001` sort à "
         "**0 échec sur 91 règles EN 16931 et 69 règles BR-FR**.", "",
         "Les références de cas (`OK-001`, `CALC-001`…) sont des "
         "identifiants du corpus, **pas** des codes de norme.", "",
         "## Les cas, groupés par ce qu'ils testent", "",
         "Le groupement suit ce que chaque cas déclenche réellement, pas la "
         "famille dont il vient. Le groupe non normé vient en premier : "
         "c'est celui qui justifie l'existence de ce corpus.", ""]

    for nature in ORDRE_NATURES:
        cas = par_nature.get(nature)
        if not cas:
            continue
        titre, intro = NATURES[nature]
        L += [f"### {titre} ({len(cas)} cas)", "", intro, ""]
        montre_assert = nature == "assertion"
        entete = ("| Réf | Cas | Attendu | Assertion |" if montre_assert
                  else "| Réf | Cas | Attendu | Référence |")
        L += [entete, "|---|---|---|---|"]
        for r in sorted(cas, key=lambda x: x["ref"]):
            derniere = (r["assertions_declenchees"] if montre_assert
                        else r["regle"])
            L.append(f"| `{r['ref']}` | {r['titre']} | {r['attendu']} | "
                     f"{derniere} |")
        L.append("")

    L += ["## Ce que ce corpus a corrigé", "",
          "Ce corpus a d'abord été écrit de mémoire, en attribuant à chaque "
          f"cas la règle qui semblait évidente. La vérification a établi que "
          f"**{len(CORRECTIONS)} cas ne testaient pas ce qu'ils "
          "annonçaient** : règle qui tient malgré le défaut, défaut qui "
          "n'atteint jamais le XML, norme source erronée, ou assertion "
          "déclarée absente qui se déclenche pourtant. Ils sont listés ici "
          "plutôt que corrigés en silence — un corpus dont on peut vérifier "
          "les affirmations vaut mieux qu'un corpus qui n'admet rien.", "",
          "Elle s'est faite en deux passes, et la seconde a compté. Lire "
          "les schematrons en a corrigé six. **Exécuter** ensuite les "
          "validateurs sur les 32 documents a rectifié trois attributions "
          "de plus — `DATA-003` et `XML-002`, qui s'ajoutent à la liste, "
          "et `CALC-005`, que la lecture avait déjà repris une fois et "
          "classé à tort « aucune assertion ». Lire une règle et "
          "l'exécuter ne donnent pas le même résultat : c'est la leçon la "
          "plus utile de ce corpus, et elle vaut aussi pour qui "
          "l'utilisera.", ""]
    for ref, annonce, etabli in CORRECTIONS:
        L += [f"**`{ref}`** — annoncé : {annonce}.", "",
              f"Établi : {etabli}", ""]
    L += ["Trois autres cas portaient un code faux sans se tromper sur la "
          "nature du défaut : `DATA-001` et `DATA-002` citaient `BR-02` "
          "(qui concerne le numéro de facture, pas la date) alors que le "
          "contrôle du format et du calendrier vient du schematron "
          "français `BR-FR-03_BT-2` ; `CALC-004` citait la famille "
          "`BR-DEC-*` au lieu de l'assertion précise `BR-DEC-23`.", "",
          "## Renumérotation des références", "",
          "Les références de cas ont changé **une fois, avant la première "
          "publication** du corpus. Les anciens préfixes pouvaient se lire "
          "comme des codes normatifs : `BR-001` n'a jamais désigné la règle "
          "EN 16931 `BR-1`, et `FMT-` est par ailleurs utilisé par le "
          "moteur de diagnostic pour ses propres contrôles. Les références "
          "ci-dessous sont désormais stables.", "",
          "| Ancienne réf | Nouvelle réf |", "|---|---|"]
    L += [f"| `{a}` | `{n}` |" for a, n in RENOMMAGE]
    L += ["", "`OK-001`, `PDF-00x`, `XML-00x`, `PRF-00x` et `RBT-00x` sont "
          "inchangés : aucune ambiguïté possible avec un code normatif.", "",
          "## Limites", "",
          "La conformité PDF/A-3 est produite de façon approchée : le profil "
          "ICC n'est pas embarqué. Les cas concernés sont signalés. Le corpus "
          "est fiable pour tester l'extraction et la validation du XML, pas "
          "pour certifier une conformité PDF/A-3.", "",
          "## Structure", "",
          "```", "CAS-XXX/", "  facture.pdf     document complet",
          "  factur-x.xml    XML seul", "  README.md       description du défaut",
          "```", "",
          "---", "",
          "Documents fictifs, sans valeur légale. Toute ressemblance avec des "
          "entreprises existantes serait fortuite."]
    return "\n".join(L)


def commande_list():
    cas_list = catalogue()
    par_cat = {}
    for c in cas_list:
        par_cat.setdefault(c.categorie, []).append(c)
    print(f"\n{len(cas_list)} cas\n")
    for cat in sorted(par_cat):
        print(f"{cat.upper()}")
        for c in par_cat[cat]:
            print(f"  {c.ref:<9} {c.attendu:<15} {c.titre}")
        print()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("commande", choices=["list", "generate", "manifest"])
    ap.add_argument("--out", default="./corpus")
    args = ap.parse_args()

    if args.commande == "list":
        commande_list()
    elif args.commande == "generate":
        commande_generate(args.out)
    else:
        chemin = os.path.join(args.out, "manifeste.json")
        if not os.path.exists(chemin):
            sys.exit("Manifeste absent — lancer `generate` d'abord.")
        with open(chemin, encoding="utf-8") as fh:
            print(json.dumps(json.load(fh), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
