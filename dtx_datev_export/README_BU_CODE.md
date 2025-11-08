# DATEV BU-Code (Buchungsschlüssel) - Dokumentation

**Version:** 1.0
**Stand:** 08.11.2025
**Modul:** dtx_datev_export / dtx_datev_export_xml
**Autor:** Detalex GmbH

---

## ⚡ Schnellentscheidung: BU-Code exportieren oder nicht?

### 🎯 Wann BU-Code-Export AKTIVIEREN (Feld ausfüllen)?

✅ **Aktivieren Sie den BU-Code-Export, wenn:**

1. **Ihre Steuerkanzlei das ausdrücklich verlangt**
   - Die Kanzlei hat Ihnen eine Liste mit BU-Codes gegeben
   - Die Kanzlei möchte die Steuerautomatik in DATEV nutzen
   - Sie haben die BU-Codes mit der Kanzlei abgestimmt

2. **Sie komplexe Steuersituationen haben**
   - Innergemeinschaftliche Lieferungen (ig-Lieferungen)
   - §13b UStG-Fälle (Reverse Charge)
   - Unterschiedliche Steuersätze (19%, 7%, 0%)
   - Export in Drittländer

3. **Die DATEV Steuerautomatik genutzt werden soll**
   - Automatische Kontenfindung erwünscht
   - Automatische UStVA-Zuordnung gewünscht
   - Zeitersparnis beim Steuerberater

### ❌ Wann BU-Code-Export DEAKTIVIEREN (Feld leer lassen)?

✅ **Deaktivieren Sie den BU-Code-Export, wenn:**

1. **Ihre Steuerkanzlei die Steuer selbst zuordnet**
   - Die Kanzlei übernimmt die Steuerbehandlung komplett in DATEV
   - Sie haben keine BU-Code-Liste von der Kanzlei erhalten
   - Erste Zusammenarbeit - Prozesse noch nicht abgestimmt

2. **Sie unsicher sind, welche BU-Codes korrekt sind**
   - Keine klare Abstimmung mit der Kanzlei erfolgt
   - Unterschiedliche DATEV-Versionen im Einsatz
   - Risiko von falschen BU-Codes

3. **Beim ersten DATEV-Export (Testphase)**
   - Neue Mandant-Kanzlei-Beziehung
   - Erste Erfahrungen mit DATEV XML Export
   - Testlauf zur Prozessabstimmung

### 🔄 Empfohlenes Vorgehen

**Phase 1: Start ohne BU-Code (empfohlen)**
```
1. Ersten Export OHNE BU-Code durchführen
2. ZIP-Datei an Kanzlei senden
3. Feedback einholen: Import erfolgreich?
4. Prüfen: Wünscht Kanzlei BU-Codes?
```

**Phase 2: BU-Code-Liste anfordern (falls gewünscht)**
```
1. Liste der BU-Codes von Kanzlei anfordern
2. BU-Codes in Odoo-Steuern eintragen
3. Testexport mit BU-Codes durchführen
4. Kontrolle: Stimmen die Steuerkonten?
```

**Phase 3: Produktivbetrieb**
```
1. Bei erfolgreichen Tests: BU-Codes aktiviert lassen
2. Dokumentation der BU-Code-Zuordnung pflegen
3. Bei Änderungen: Mit Kanzlei abstimmen
```

### ⚠️ Wichtigste Regel

> **Sprechen Sie IMMER mit Ihrer Steuerkanzlei, bevor Sie BU-Codes aktivieren!**
> Eine falsche Steuer-Zuordnung führt zu Fehlern in der Umsatzsteuervoranmeldung.

---

## 📋 Inhaltsverzeichnis

1. [Was ist der BU-Code?](#was-ist-der-bu-code)
2. [Technischer Aufbau](#technischer-aufbau)
3. [Praktische Bedeutung für den DATEV-Export](#praktische-bedeutung-für-den-datev-export)
4. [Wie wird der BU-Code verwendet?](#wie-wird-der-bu-code-verwendet)
5. [Export-Verhalten in Odoo](#export-verhalten-in-odoo)
6. [Was passiert in DATEV?](#was-passiert-in-datev)
7. [Konfliktszenarien und Lösungen](#konfliktszenarien-und-lösungen)
8. [Abstimmung mit der Steuerkanzlei](#abstimmung-mit-der-steuerkanzlei)
9. [Best Practices](#best-practices)
10. [Häufige Fragen (FAQ)](#häufige-fragen-faq)

---

## Was ist der BU-Code?

### Definition

Der **BU-Code** (auch **Buchungsschlüssel** genannt) ist ein 4-stelliger numerischer Code, der in DATEV zur **automatischen Steuerung von Buchungsvorgängen** verwendet wird.

**BU** steht dabei für:
- **B** = **Berichtigungsschlüssel** (1. Stelle)
- **U** = **Umsatzsteuerschlüssel** (2.-4. Stelle bzw. 2. Stelle)

### Verbindung zur DATEV Steuerautomatik

Der BU-Code ist das **zentrale Steuerelement** der **DATEV Steuerautomatik**:

- 🔄 **Automatische Kontenfindung:** DATEV wählt automatisch das richtige Steuer-Sachkonto
- 📊 **Automatische Steuerberechnung:** Der Steuerbetrag wird automatisch ermittelt
- 📝 **Automatische UStVA-Zuordnung:** Steuerbeträge werden automatisch der Umsatzsteuervoranmeldung zugeordnet
- ⚖️ **Automatische Gegenbuchung:** Das Steuerkonto wird automatisch als Gegenkonto gebucht

> 💡 **Die DATEV Steuerautomatik** arbeitet nach dem Prinzip: **"Ein Code steuert alles"**
> Der BU-Code enthält alle Informationen, die DATEV benötigt, um die Buchung steuerlich korrekt zu verarbeiten.

### Beispiele für gängige BU-Codes

| BU-Code | Bedeutung | Verwendung |
|---------|-----------|------------|
| `0` oder leer | Keine Steuer | Steuerfreie Umsätze |
| `1` | 7% USt | Ermäßigter Steuersatz (z.B. Bücher, Lebensmittel) |
| `2` | 19% USt | Normaler Steuersatz |
| `3` | 19% USt | Normal mit Vorsteuerabzug |
| `40` | 0% ig-Lieferung | Innergemeinschaftliche Lieferung |
| `8` | 7% VSt | Vorsteuer bei ermäßigtem Satz |
| `9` | 19% VSt | Vorsteuer bei Normalsteuersatz |

> **Wichtig:** Die genauen BU-Codes können sich zwischen verschiedenen DATEV-Versionen und -Konfigurationen unterscheiden und werden in der Regel von der Steuerkanzlei festgelegt.

---

## Technischer Aufbau

### Struktur des BU-Codes

Der BU-Code besteht aus maximal **4 Ziffern** (Typ: `unsignedShort`, Wertebereich: 0-9999):

```
Format: [B][UUU] oder [B][U]
        ↑   ↑      ↑  ↑
        |   |      |  |
        |   |      |  └─ Umsatzsteuerschlüssel (1-stellig)
        |   └────────── Umsatzsteuerschlüssel (3-stellig)
        └────────────── Berichtigungsschlüssel (optional)
```

### Beispiele:

- **`0`** oder **leer**: Keine Steuer, kein Berichtigungsschlüssel
- **`9`**: Kein Berichtigungsschlüssel, Umsatzsteuerschlüssel = 9 (19% Vorsteuer)
- **`40`**: Kein Berichtigungsschlüssel, Umsatzsteuerschlüssel = 40 (ig-Lieferung)
- **`119`**: Berichtigungsschlüssel = 1, Umsatzsteuerschlüssel = 19

### XSD-Definition (aus DATEV-Schema)

```xml
<xsd:simpleType name="p10033">
    <xsd:documentation>Name: Berichtigungs-/Umsatzsteuerschlüssel</xsd:documentation>
    <xsd:documentation>English Name: Adjustment code/value added tax code</xsd:documentation>
    <xsd:restriction base="xsd:unsignedShort">
        <xsd:totalDigits value="4"/>
        <xsd:minInclusive value="0"/>
        <xsd:maxInclusive value="9999"/>
    </xsd:restriction>
</xsd:simpleType>
```

---

## Praktische Bedeutung für den DATEV-Export

### Die DATEV Steuerautomatik im Detail

Der BU-Code ist das **Herzstück der DATEV Steuerautomatik**. Bei Verwendung eines BU-Codes passiert in DATEV Folgendes automatisch:

#### 1. **Automatische Kontenfindung**
   - DATEV ermittelt das passende **Steuer-Sachkonto** (z.B. 1576 für 19% Vorsteuer)
   - Das Gegenkonto wird automatisch gesetzt
   - Keine manuelle Konteneingabe erforderlich

#### 2. **Automatische Steuerberechnung**
   - Der **Steuerbetrag** wird aus dem Nettobetrag berechnet
   - Rundungsdifferenzen werden korrekt behandelt
   - Bruttobeträge werden automatisch ermittelt

#### 3. **Automatische Splittbuchung**
   - Die Buchung wird in **zwei Buchungszeilen** aufgeteilt:
     - Zeile 1: Nettobetrag auf Sachkonto (z.B. 4400 Erlöse)
     - Zeile 2: Steuerbetrag auf Steuerkonto (z.B. 1776 USt 19%)
   - Beide Zeilen werden automatisch verknüpft

#### 4. **Automatische UStVA-Zuordnung**
   - Steuerbeträge werden der **Umsatzsteuervoranmeldung** (UStVA) zugeordnet
   - Zuordnung zur richtigen **Kennziffer** erfolgt automatisch
   - Summen werden für die UStVA aufbereitet

#### 5. **Automatische Steuerprüfung**
   - DATEV prüft die **Plausibilität** der Steuerbuchung
   - Warnung bei unüblichen Konstellationen
   - Validierung der Steuersätze

### Hauptfunktionen des BU-Codes

Der BU-Code steuert in DATEV **automatisch**:

1. **Steuerberechnung und -buchung**
   - Automatische Ermittlung des korrekten Steuersatzes
   - Buchung auf das richtige Steuer-Sachkonto
   - Steuervoranmeldung (UVA) wird automatisch befüllt

2. **Gegenkonto-Automatik**
   - DATEV wählt automatisch das passende Steuerkonto
   - Unterscheidung zwischen Umsatzsteuer und Vorsteuer

3. **Compliance und Steuerrecht**
   - Korrekte Behandlung von Sonderfällen (ig-Lieferungen, §13b UStG, etc.)
   - Automatische Zuordnung zu UStVA-Kennziffern

### Wo wird der BU-Code verwendet?

Im **DATEV XML Export** wird der BU-Code bei **jeder Rechnungszeile** (invoice_item) im Element `<accounting_info>` übertragen:

```xml
<accounting_info
    account_no="8400"
    cost_category_id="100"
    booking_text="IT-Beratungsleistung"
    bu_code="9"
/>
```

**Bedeutung in Odoo:**
- Der BU-Code wird aus dem Feld `l10n_de_datev_code` der verwendeten **Steuer** (`account.tax`) übernommen
- Das Feld ist im Steuerformular unter **"Erweiterte Optionen"** als **"DATEV-Buchungsschlüssel (BU-Code)"** sichtbar

---

## Wie wird der BU-Code verwendet?

### In Odoo konfigurieren

#### Schritt 1: Steuer öffnen
1. Menü: **Buchhaltung** → **Konfiguration** → **Steuern**
2. Gewünschte Steuer auswählen (z.B. "19% Vorsteuer")

#### Schritt 2: BU-Code eintragen
1. Tab **"Erweiterte Optionen"** öffnen
2. Feld **"DATEV-Buchungsschlüssel (BU-Code)"** ausfüllen
3. Beispiel: Für 19% Vorsteuer → `9` eintragen
4. Speichern

#### Schritt 3: In Rechnung verwenden
- Bei Erstellung einer Rechnung wird die Steuer ausgewählt
- Der BU-Code wird automatisch aus der Steuer übernommen
- Beim Export wird er zur jeweiligen Rechnungszeile hinzugefügt

### Automatische Übernahme beim Export

```python
# Im XML-Template (views/templates.xml):
<accounting_info
    t-att-bu_code="line.tax_ids.l10n_de_datev_code or False"
/>
```

**Ablauf:**
1. Rechnungszeile hat Steuer → `line.tax_ids.l10n_de_datev_code` wird gelesen
2. Wert wird ins XML-Attribut `bu_code` geschrieben
3. DATEV liest beim Import den BU-Code und verarbeitet ihn

---

## Export-Verhalten in Odoo

### Wann wird der BU-Code exportiert?

Der BU-Code wird **nur dann exportiert**, wenn:

✅ **Voraussetzungen erfüllt:**
- Die Rechnungszeile hat eine Steuer (`line.tax_ids`)
- Die Steuer hat einen BU-Code (`l10n_de_datev_code` ist ausgefüllt)
- Der BU-Code ist nicht leer

❌ **Nicht exportiert, wenn:**
- Keine Steuer auf der Rechnungszeile
- BU-Code-Feld in der Steuer ist leer
- Mehrfachbesteuerung auf einer Zeile (wird als Fehler erkannt)

### XML-Ausgabe Beispiele

**Mit BU-Code:**
```xml
<accounting_info
    account_no="4400"
    booking_text="Beratungsleistung"
    bu_code="9"
/>
```

**Ohne BU-Code (leer):**
```xml
<accounting_info
    account_no="4400"
    booking_text="Beratungsleistung"
/>
```

> **Hinweis:** Das Attribut `bu_code` ist im DATEV-Schema als **`optional`** definiert. Es ist also **nicht zwingend erforderlich** für einen validen Export.

---

## Was passiert in DATEV?

### Szenario 1: BU-Code wird aus Odoo exportiert

**Situation:**
- Odoo sendet BU-Code `9` (19% Vorsteuer)
- Export-XML enthält: `bu_code="9"`

**DATEV-Verhalten:**
1. **Import der Rechnung**
   - DATEV liest den BU-Code aus dem XML
   - Prüfung, ob BU-Code `9` in DATEV konfiguriert ist

2. **Wenn BU-Code in DATEV vorhanden:**
   - ✅ DATEV verwendet den **exportierten BU-Code**
   - Automatische Buchung auf Vorsteuer-Sachkonto (z.B. 1576)
   - Steuerberechnung erfolgt gemäß BU-Code-Konfiguration

3. **Wenn BU-Code in DATEV NICHT vorhanden:**
   - ⚠️ DATEV zeigt **Importfehler** oder **Warnmeldung**
   - Import kann fehlschlagen oder muss manuell nachbearbeitet werden
   - Steuerberater muss den BU-Code in DATEV anlegen oder Buchung korrigieren

### Szenario 2: BU-Code wird NICHT aus Odoo exportiert

**Situation:**
- Odoo sendet **keinen BU-Code** (Feld leer oder nicht gesetzt)
- Export-XML enthält: `<accounting_info ... />` (ohne `bu_code`)

**DATEV-Verhalten:**
1. **Import der Rechnung**
   - DATEV liest die Buchungsinformationen
   - **Kein BU-Code vorhanden**

2. **Automatische Zuordnung:**
   - ⚙️ DATEV versucht, den BU-Code **automatisch zu ermitteln**
   - Basis: Kontonummer, Betrag, Gegenkonto
   - Falls Automatik erfolgreich: Buchung wird korrekt durchgeführt

3. **Manuelle Nacharbeit:**
   - ❗ Falls DATEV die Steuer nicht automatisch erkennen kann:
   - Steuerberater muss den BU-Code **manuell nachtragen**
   - Erhöhter Aufwand bei der Buchführung
   - Verzögerung bei der Buchhaltung

---

## Konfliktszenarien und Lösungen

### Konflikt 1: BU-Code in Odoo vs. DATEV unterschiedlich

**Problem:**
- In Odoo ist für 19% Vorsteuer der BU-Code `9` hinterlegt
- In DATEV verwendet die Kanzlei für 19% Vorsteuer den BU-Code `3`

**Konsequenz:**
- ⚠️ DATEV importiert mit BU-Code `9`
- Buchung erfolgt möglicherweise auf **falsches Steuerkonto**
- Steuervoranmeldung wird **fehlerhaft befüllt**

**Lösung:**
1. **Abstimmung mit Steuerkanzlei** (siehe unten)
2. **Odoo anpassen:** BU-Code in Odoo auf `3` ändern
3. **Alternative:** BU-Code in Odoo leer lassen und DATEV entscheiden lassen

### Konflikt 2: BU-Code in Odoo, aber in DATEV nicht konfiguriert

**Problem:**
- Odoo exportiert BU-Code `40` (ig-Lieferung)
- DATEV-System der Kanzlei kennt BU-Code `40` nicht

**Konsequenz:**
- ❌ **Import-Fehler** in DATEV
- Buchungsstapel wird nicht automatisch verarbeitet
- Manuelle Korrektur erforderlich

**Lösung:**
1. **Steuerberater informieren:** BU-Code `40` in DATEV anlegen
2. **Fallback:** BU-Code in Odoo für diese Steuer entfernen
3. **Dokumentation:** Liste aller verwendeten BU-Codes an Kanzlei senden

### Konflikt 3: Mehrfachbesteuerung in Odoo

**Problem:**
- Eine Rechnungszeile hat **mehrere Steuern** gleichzeitig
- Jede Steuer hätte einen eigenen BU-Code

**Konsequenz:**
- ❌ Odoo erkennt dies als **Fehler**
- Export wird mit Fehlermeldung abgebrochen
- Validierung schlägt fehl

**Lösung:**
- ✅ **Odoo-Design:** Pro Zeile nur **eine Steuer** verwenden
- Alternative: Zusammengesetzte Steuern (`amount_type='group'`) nutzen
- Falls mehrere Steuern nötig: Separate Rechnungszeilen erstellen

---

## Abstimmung mit der Steuerkanzlei

### ⚠️ WICHTIG: Vorab-Klärung erforderlich!

**Vor dem ersten DATEV-Export sollte mit der Steuerkanzlei geklärt werden:**

### Checkliste für die Abstimmung

#### 1. **Wird der BU-Code überhaupt benötigt?**

**Fragen an die Kanzlei:**
- ❓ "Sollen wir den BU-Code in den XML-Exporten mitliefern?"
- ❓ "Oder übernehmen Sie die Steuer-Zuordnung selbst in DATEV?"

**Mögliche Antworten:**
- ✅ **"Ja, bitte BU-Code mitliefern"** → BU-Codes in Odoo konfigurieren
- ✅ **"Nein, wir erledigen das in DATEV"** → BU-Codes in Odoo leer lassen

#### 2. **Welche BU-Codes verwendet die Kanzlei?**

**Erforderliche Informationen:**
- Komplette **Liste der BU-Codes** der Kanzlei anfordern
- Zuordnung: Welcher BU-Code für welche Steuerart?

**Beispiel-Tabelle zur Abstimmung:**

| Steuerart in Odoo | Steuersatz | BU-Code Kanzlei | In Odoo eintragen |
|-------------------|------------|-----------------|-------------------|
| Umsatzsteuer (Verkauf) | 19% | `3` | ✅ Ja |
| Umsatzsteuer (Verkauf) | 7% | `2` | ✅ Ja |
| Vorsteuer (Einkauf) | 19% | `8` | ✅ Ja |
| Vorsteuer (Einkauf) | 7% | `9` | ✅ Ja |
| Steuerfreie Lieferung | 0% | `0` oder leer | ❌ Leer lassen |
| ig-Lieferung EU | 0% | `41` | ✅ Ja |

#### 3. **Testlauf durchführen**

**Vorgehen:**
1. **Testrechnung erstellen** in Odoo
2. **Export als ZIP-Datei** generieren
3. **An Kanzlei senden** mit Bitte um Probe-Import
4. **Feedback einholen:**
   - Wurden die Buchungen korrekt importiert?
   - Stimmen die Steuerkonten?
   - Ist die UStVA korrekt befüllt?

#### 4. **Dokumentation erstellen**

**Wichtig für beide Seiten:**
- 📄 **Schriftliche Vereinbarung** über verwendete BU-Codes
- 📋 **Aktualisierung bei Änderungen** (z.B. neuer Steuersatz)
- 🔄 **Regelmäßige Überprüfung** (z.B. jährlich)

---

## Best Practices

### Empfohlene Vorgehensweise

#### 1. **Start ohne BU-Code**
- ✅ **Empfehlung:** Zunächst **ohne BU-Code** exportieren
- DATEV übernimmt automatisch die Steuer-Zuordnung
- Weniger Fehlerquellen in der Anfangsphase

#### 2. **Schrittweise Einführung**
- Nach erfolgreichen Test-Exporten
- BU-Codes **nach und nach** hinzufügen
- Mit den häufigsten Steuern beginnen (19% USt/VSt)

#### 3. **Konsistenz sicherstellen**
- Alle Steuern einer Art mit **gleichem BU-Code** versehen
- Beispiel: Alle "19% Vorsteuer"-Steuern → BU-Code `9`
- Keine unterschiedlichen Codes für dieselbe Steuerart

#### 4. **Dokumentation pflegen**
- ✅ **Internes Dokument** mit BU-Code-Zuordnung führen
- Bei Änderungen: Abstimmung mit Kanzlei
- Teil der Buchhaltungs-Prozessdokumentation

#### 5. **Regelmäßige Validierung**
- Export mit **XSD-Validierung aktiviert** durchführen
- Fehler sofort beheben
- Testexporte vor Produktiv-Übertragung

---

## Häufige Fragen (FAQ)

### Allgemeine Fragen

**Q: Muss ich den BU-Code zwingend ausfüllen?**
**A:** Nein. Das Feld ist **optional**. DATEV kann die Steuer auch automatisch zuordnen. Eine Abstimmung mit der Steuerkanzlei ist aber empfehlenswert.

---

**Q: Was passiert, wenn ich den falschen BU-Code exportiere?**
**A:** Die Buchung wird in DATEV auf ein **falsches Steuerkonto** gebucht. Dies führt zu Fehlern in der Steuervoranmeldung. Die Kanzlei muss die Buchungen manuell korrigieren.

---

**Q: Kann ich den BU-Code später noch ändern?**
**A:** Ja, aber:
- ⚠️ **Bereits exportierte Rechnungen** sind nicht betroffen
- ✅ **Neue Exporte** verwenden den aktualisierten BU-Code
- 🔄 Bei Änderungen: Kanzlei informieren!

---

**Q: Wo finde ich die BU-Codes meiner Steuerkanzlei?**
**A:** Die BU-Codes werden von der **Steuerkanzlei** in DATEV konfiguriert. Sie müssen **direkt bei der Kanzlei** nachfragen und eine Liste anfordern.

---

**Q: Kann ich den BU-Code pro Rechnung ändern?**
**A:** Nein. Der BU-Code ist an die **Steuer** gekoppelt, nicht an die Rechnung. Wenn unterschiedliche BU-Codes nötig sind, müssen **verschiedene Steuern** angelegt werden.

---

### Technische Fragen

**Q: Wird der BU-Code validiert?**
**A:** Ja, beim Export mit aktivierter **XSD-Validierung** wird geprüft:
- ✅ Format: 0-9999 (4-stellig, numerisch)
- ❌ **Nicht** geprüft: Ob der Code in DATEV existiert (das prüft erst DATEV selbst)

---

**Q: Was bedeutet `bu_code="0"`?**
**A:** `0` bedeutet **"keine Steuer"** bzw. **"kein Umsatzsteuerschlüssel benötigt"**. Wird für steuerfreie Umsätze verwendet.

---

**Q: Kann eine Zeile mehrere BU-Codes haben?**
**A:** Nein. Pro Rechnungszeile kann nur **ein BU-Code** exportiert werden. Odoo blockiert Rechnungen mit mehreren Steuern pro Zeile beim Export.

---

**Q: Wo im XML steht der BU-Code?**
**A:** Im Element `<accounting_info>` als Attribut `bu_code`:
```xml
<invoice_item_list>
    <accounting_info bu_code="9" ... />
</invoice_item_list>
```

---

### Prozess-Fragen

**Q: Muss ich bei jedem Export neu abstimmen?**
**A:** Nein. Die **initiale Abstimmung** mit der Kanzlei reicht. Nur bei **Änderungen** (neue Steuern, neue Steuersätze) ist eine erneute Abstimmung nötig.

---

**Q: Was passiert bei einem DATEV-Update der Kanzlei?**
**A:** Bei DATEV-Updates **können sich BU-Codes ändern**. Nach größeren Updates der Kanzlei sollte die BU-Code-Liste **erneut abgestimmt** werden.

---

**Q: Kann die Kanzlei den BU-Code in DATEV überschreiben?**
**A:** Ja. Der Steuerberater kann in DATEV **jeden importierten BU-Code manuell ändern**. Das sollte aber die Ausnahme sein, nicht die Regel.

---

## Zusammenfassung

### ✅ Die wichtigsten Punkte

1. **BU-Code ist das Herzstück der DATEV Steuerautomatik**
2. **BU-Code ist optional** im DATEV-Export
3. **Abstimmung mit Steuerkanzlei ist essentiell**
4. **Start ohne BU-Code** ist oft der sicherste Weg
5. **Schrittweise Einführung** nach erfolgreichen Tests
6. **Konsistenz und Dokumentation** sind wichtig

### 🎯 Handlungsempfehlung

**Vor dem ersten Export:**
1. ✅ Gespräch mit Steuerkanzlei führen
2. ✅ Entscheidung treffen: Mit oder ohne BU-Code?
3. ✅ Falls mit BU-Code: Liste der Codes anfordern
4. ✅ Testlauf durchführen
5. ✅ Feedback einholen und anpassen

---

## Weiterführende Ressourcen

### DATEV Steuerautomatik

Die DATEV Steuerautomatik ist in folgenden Ressourcen dokumentiert:

- **DATEV Help-Center:** https://www.datev.de/hilfe
  Suchen Sie nach: "Steuerautomatik", "BU-Schlüssel", "Buchungsschlüssel"

- **DATEV FIBU-Handbuch:**
  Kapitel "Steuerautomatik" und "Buchungsschlüssel"
  Verfügbar über das DATEV Service-Portal (Login erforderlich)

- **DATEV Schnittstellen-Dokumentation:**
  https://www.datev.de/web/de/service/schnittstellen/
  Technische Details zur XML-Schnittstelle

### Support-Kontakte

**Für Odoo/BU-Code-Konfiguration:**
- **Detalex Support:** support@detalex.de
- **Modul-Dokumentation:** dtx_datev_export / dtx_datev_export_xml

**Für DATEV Steuerautomatik:**
- **Ihre Steuerkanzlei:** Beste Anlaufstelle für BU-Code-Listen
- **DATEV-Hotline:** https://www.datev.de/web/de/service/service-hotline/
- **DATEV Help-Center:** https://www.datev.de/hilfe

---

**© 2025 Detalex GmbH - Alle Rechte vorbehalten**
