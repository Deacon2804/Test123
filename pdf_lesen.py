import fitz  # PyMuPDF zum PDF-Auslesen
import re  # Reguläre Ausdrücke für die Werkzeugnummer-Suche

# 🔹 Datei-Pfad zur PDF
pdf_datei = "/Users/macbook/Desktop/Programm/werkzeuge.pdf"

# --------------------------------------------------
# 🔍 FUNKTION: Suche nach Werkzeug in der PDF
# --------------------------------------------------
def suche_werkzeug(werkzeugnummer, pfad):
    """Sucht eine Werkzeugnummer in der PDF und gibt die relevanten Werte zurück."""
    try:
        doc = fitz.open(pfad)  # 📄 PDF öffnen
        daten_dict = {}  # 📊 Speichert die extrahierten Werte
        kr_wert, kl_wert = None, None  # Standardwerte für KR/KL

        # 🔹 Falls Werkzeugnummer mit '2', '3', '4' endet → Erst Werkzeug '1' suchen
        if werkzeugnummer[-1] in "23456789":
            basis_werkzeug = werkzeugnummer[:-1] + "1"  # Ersetze letzte Ziffer mit '1'
            print(f"\n🔎 Suche nach Basis-Werkzeug {basis_werkzeug}, um KR/KL zu speichern...")

            # Suche zuerst nach Werkzeug '1'
            basis_daten = suche_werkzeug(basis_werkzeug, pfad)
            if basis_daten:
                # 📌 KR/KL aus dem Basis-Werkzeug speichern
                for _, werte in basis_daten.items():
                    kr_wert = werte.get("KR", None)
                    kl_wert = werte.get("KL", None)
                print(f"✅ KR/KL von {basis_werkzeug} gespeichert: KR = {kr_wert}, KL = {kl_wert}\n")
            else:
                print(f"⚠️ Fehler: KR und KL von Werkzeug {basis_werkzeug} wurden nicht gefunden!")

        # --------------------------------------------------
        # 🔍 PDF DURCHSUCHEN
        # --------------------------------------------------
        for seiten_nr, seite in enumerate(doc, start=1):
            text = seite.get_text("text")  # 📄 Text aus Seite extrahieren
            zeilen = [z.strip() for z in text.split("\n") if z.strip()]  # Leerzeichen entfernen

            # 🔹 Prüfen, ob die Werkzeugnummer in dieser Seite vorkommt
            for i, zeile in enumerate(zeilen):
                if re.search(rf"T:\s*{werkzeugnummer}\b", zeile):  # **Exakte Werkzeugnummer suchen**
                    print(f"\n✅ Werkzeugnummer {werkzeugnummer} gefunden auf Seite {seiten_nr}!\n")
                    werte = {"T": werkzeugnummer}

                    # 📌 Werte aus den folgenden Zeilen extrahieren
                    for j in range(i + 1, len(zeilen)):  # Nachfolgende Zeilen durchsuchen
                        match = re.match(r"(K|R|KR|L|KL)\s*:\s*([\d.,-]+|[A-Za-zäöüÄÖÜ\s]+)", zeilen[j])
                        if match:
                            key, value = match.groups()
                            werte[key] = value.strip()
                        elif re.match(r"T:\s*\d+", zeilen[j]):  # Stoppe, wenn ein neues Werkzeug kommt
                            break

                    # Falls KR/KL noch fehlen → Werte aus Basis-Werkzeug verwenden
                    if werkzeugnummer[-1] in "23456789":
                        werte.setdefault("KR", kr_wert)
                        werte.setdefault("KL", kl_wert)

                    daten_dict[seiten_nr] = werte  # 📊 Speichert die gefundenen Werte für diese Seite
                    break  # **Stoppe, wenn Werkzeug gefunden wurde**

        return daten_dict  # ✅ Gibt die extrahierten Werte zurück

    except Exception as e:
        print(f"❌ Fehler beim Lesen der PDF: {e}")
        return None

# --------------------------------------------------
# 🔥 HAUPTPROGRAMM
# --------------------------------------------------
if __name__ == "__main__":
    werkzeugnummer = input("🔍 Welche Werkzeugnummer suchst du? ").strip()

    # 🔍 PDF durchsuchen
    daten = suche_werkzeug(werkzeugnummer, pdf_datei)

    # ✅ Ergebnisse anzeigen
    if daten:
        for seite, werte in daten.items():
            print(f"\n📄 Werte auf Seite {seite}:")
            for key, value in werte.items():
                print(f"   {key}: {value}")
            print("-" * 50)
    else:
        print("⚠️ Konnte keine passenden Einträge in der PDF finden.")