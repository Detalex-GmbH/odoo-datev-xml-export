# 🚨 WICHTIGE NOTIZEN - DATEV XML Export

## ⚠️ KRITISCHE ÄNDERUNGEN - BITTE LESEN!

### 📅 Datum: 15. Oktober 2025

---

## 🆕 NEUE FEATURES

### ✅ Dokumententyp-Filter (Checkboxen)
**Location**: `datev_export.py` + `datev_export_views.xml`

**Neue Felder im Model**:
```python
include_out_invoice = fields.Boolean("Ausgehende Rechnungen", default=True)
include_out_refund = fields.Boolean("Ausgehende Gutschriften", default=True)
include_in_invoice = fields.Boolean("Eingehende Rechnungen", default=True)
include_in_refund = fields.Boolean("Eingehende Gutschriften", default=True)
```

**Wichtig**:
- ✅ Alle Checkboxen sind standardmäßig AKTIV (default=True)
- ✅ Mindestens EINE Checkbox muss aktiviert sein (Validation in `get_invoices()`)
- ✅ Filter wird in `get_invoices()` angewendet über `move_type IN (...)` Query
- ✅ Beschreibung zeigt ausgewählte Typen an (`get_description()`)

---

## 🔧 GEÄNDERTE METHODEN

### 1️⃣ `get_invoices()` - WICHTIGSTE ÄNDERUNG!
**Was wurde geändert**:
```python
# NEU: move_types Liste wird dynamisch aufgebaut
move_types = []
if self.include_out_invoice:
    move_types.append('out_invoice')
# ... etc

# NEU: Validation
if not move_types:
    raise UserError(_("Keine Dokumententypen ausgewählt!"))

# NEU: Filter hinzugefügt
search_clause.append(("move_type", "in", move_types))
```

**⚠️ ACHTUNG**:
- Methode wird bei `write()` automatisch aufgerufen wenn `date_start` oder `date_stop` geändert wird
- Methode wird bei `create()` automatisch aufgerufen
- **MUSS** immer mindestens einen move_type zurückgeben

---

### 2️⃣ `get_description()`
**Was wurde geändert**:
```python
# NEU: Dokumententypen werden dynamisch aufgebaut
doc_types = []
if self.include_out_invoice:
    doc_types.append("Ausgehende Rechnungen")
# ... etc

doc_types_str = ", ".join(doc_types) if doc_types else "Alle Dokumententypen"
```

**Verwendung**:
- Wird in ZIP-Attachment Description verwendet
- Wird in Chatter-Nachricht verwendet
- Zeigt User welche Typen exportiert wurden

---

### 3️⃣ `write()` - BESTEHENDE LOGIK!
**⚠️ WICHTIG - NICHT ÄNDERN**:
```python
def write(self, vals):
    res = super().write(vals)
    if any(changed_value in vals for changed_value in ["date_start", "date_stop"]):
        for record in self:
            # AUTOMATISCHES RE-FETCH der Invoices!
            super().write({"invoice_ids": [(6, 0, record.get_invoices().ids)]})
    return res
```

**Das bedeutet**:
- ✅ Bei Änderung von `date_start` → Invoices werden NEU geladen
- ✅ Bei Änderung von `date_stop` → Invoices werden NEU geladen
- ❓ **FRAGE**: Sollten auch die Checkboxen hier rein?
  ```python
  # MÖGLICHE ERWEITERUNG:
  if any(changed_value in vals for changed_value in [
      "date_start", "date_stop",
      "include_out_invoice", "include_out_refund",  # NEU?
      "include_in_invoice", "include_in_refund"     # NEU?
  ]):
  ```

---

## 📝 VIEW ÄNDERUNGEN

### Neue Group "Dokumententyp-Filter"
**Location**: `datev_export_views.xml`

```xml
<group string="Dokumententyp-Filter">
    <field name="include_out_invoice" readonly="state != 'draft'"/>
    <field name="include_out_refund" readonly="state != 'draft'"/>
    <field name="include_in_invoice" readonly="state != 'draft'"/>
    <field name="include_in_refund" readonly="state != 'draft'"/>
</group>
```

**⚠️ WICHTIG**:
- Checkboxen sind nur im `draft` State editierbar
- Sonst readonly (Konsistenz!)

---

## 🧪 TESTS SCHREIBEN!

### Test-Cases die abgedeckt werden MÜSSEN:

#### ✅ Test 1: Alle Typen aktiviert (Standard)
```python
def test_get_invoices_all_types(self):
    """Standard: Alle 4 Checkboxen aktiv → alle move_types"""
    export = self.create_export(
        include_out_invoice=True,
        include_out_refund=True,
        include_in_invoice=True,
        include_in_refund=True
    )
    invoices = export.get_invoices()
    # Erwarte: out_invoice, out_refund, in_invoice, in_refund
```

#### ✅ Test 2: Nur Ausgehende
```python
def test_get_invoices_only_outgoing(self):
    """Nur out_invoice + out_refund"""
    export = self.create_export(
        include_out_invoice=True,
        include_out_refund=True,
        include_in_invoice=False,  # DEAKTIVIERT
        include_in_refund=False    # DEAKTIVIERT
    )
    invoices = export.get_invoices()
    # Erwarte: NUR out_invoice, out_refund
    self.assertNotIn('in_invoice', invoices.mapped('move_type'))
```

#### ✅ Test 3: Nur Eingehende
```python
def test_get_invoices_only_incoming(self):
    """Nur in_invoice + in_refund"""
```

#### ✅ Test 4: Keine Checkbox aktiv → UserError
```python
def test_get_invoices_none_selected_raises_error(self):
    """Alle Checkboxen FALSE → muss UserError werfen!"""
    export = self.create_export(
        include_out_invoice=False,
        include_out_refund=False,
        include_in_invoice=False,
        include_in_refund=False
    )
    with self.assertRaises(UserError) as cm:
        export.get_invoices()
    self.assertIn("Keine Dokumententypen", str(cm.exception))
```

#### ✅ Test 5: Description zeigt richtige Typen
```python
def test_get_description_shows_selected_types(self):
    """Beschreibung enthält nur ausgewählte Typen"""
    export = self.create_export(
        include_out_invoice=True,
        include_out_refund=False,
        include_in_invoice=True,
        include_in_refund=False
    )
    description = export.get_description()
    self.assertIn("Ausgehende Rechnungen", description)
    self.assertNotIn("Ausgehende Gutschriften", description)
    self.assertIn("Eingehende Rechnungen", description)
    self.assertNotIn("Eingehende Gutschriften", description)
```

#### ✅ Test 6: Checkbox-Änderung im Draft
```python
def test_checkbox_change_in_draft_allowed(self):
    """Im draft State können Checkboxen geändert werden"""
    export = self.create_export(state='draft')
    export.write({'include_out_refund': False})
    self.assertFalse(export.include_out_refund)
```

#### ✅ Test 7: Checkbox-Änderung nach Draft verboten
```python
def test_checkbox_readonly_after_draft(self):
    """Nach draft State sind Checkboxen readonly (View-Level)"""
    # HINWEIS: Dieser Test prüft View-Logik, nicht Model-Logik!
```

---

## 🐛 BEKANNTE EDGE CASES

### 1. User deaktiviert alle Checkboxen
**Symptom**: UserError beim Speichern
**Lösung**: ✅ Bereits implementiert in `get_invoices()`

### 2. Datum-Änderung lädt Invoices neu
**Symptom**: `invoice_ids` werden überschrieben
**Frage**: Sollen Checkbox-Änderungen auch Auto-Reload triggern?
**Status**: ⚠️ UNKLAR - Entscheidung nötig!

### 3. State != 'draft' + Checkbox-Änderung
**Symptom**: View macht Feld readonly
**Verhalten**: Gut so! Verhindert Inkonsistenzen

---

## 📊 MIGRATION / UPGRADE NOTES

### Für bestehende DATEV Exports:
```sql
-- Standard-Werte setzen für bestehende Records
UPDATE datev_export_xml
SET
    include_out_invoice = TRUE,
    include_out_refund = TRUE,
    include_in_invoice = TRUE,
    include_in_refund = TRUE
WHERE
    include_out_invoice IS NULL;
```

**⚠️ WICHTIG**:
- Alle bestehenden Exports bekommen alle Checkboxen = TRUE
- Entspricht dem alten Verhalten (alle Typen wurden exportiert)
- KEINE Breaking Changes für User!

---

## 🔍 DEBUGGING TIPPS

### Problem: "Keine Invoices gefunden"
**Check**:
1. Sind Checkboxen aktiviert? → `export.include_out_invoice` etc.
2. Logging in `get_invoices()`:
   ```python
   _logger.info("DATEV: Selected move_types: %s", move_types)
   _logger.info("DATEV: Found %s invoices", len(result))
   ```

### Problem: "Falsche Invoices im Export"
**Check**:
1. Welche `move_type` haben die Invoices?
2. Stimmt `search_clause` mit Checkboxen überein?
3. Debug SQL Query:
   ```python
   query = self.env["account.move"]._where_calc(search_clause)
   _logger.info("DATEV SQL: %s", query)
   ```

---

## 🧪 ODOO TEST-TAGS REFERENZ

### � Test-Tag Syntax (3 wichtigste Varianten)
| Syntax | Bedeutung | Verwendung |
|--------|-----------|------------|
| `/dtx_datev_export_xml` | Alle Tests des Addons | Vollständiger Addon-Test |
| `.test_method_name` | Einzelne Test-Methode | Schnellster Weg für einzelne Tests |
| `/dtx_datev_export_xml:TestClassName` | Alle Tests einer Klasse | Komplette Test-Klasse |

### 📝 Vollständige Test-Befehle

#### 1️⃣ Alle Tests des Addons ausführen
```bash
docker exec -it --user root detalex_apps_18-odoo-web-1 usr/bin/odoo \
  --db_host=postgresdb \
  --db_password=Pa55w0rd \
  --config=/etc/odoo/odoo.conf \
  -d test_detalex_datev_export \
  --test-enable \
  --stop-after-init \
  --without-demo=all \
  -i dtx_datev_export_xml \
  --test-tags /dtx_datev_export_xml
```

#### 2️⃣ Einzelnen Test ausführen (Kurzform)
```bash
docker exec -it --user root detalex_apps_18-odoo-web-1 usr/bin/odoo \
  --db_host=postgresdb \
  --db_password=Pa55w0rd \
  --config=/etc/odoo/odoo.conf \
  -d test_detalex_datev_export \
  --test-enable \
  --stop-after-init \
  --without-demo=all \
  -i dtx_datev_export_xml \
  --test-tags .test_get_invoices_all_types
```

#### 3️⃣ Alle Tests einer Test-Klasse ausführen
```bash
docker exec -it --user root detalex_apps_18-odoo-web-1 usr/bin/odoo \
  --db_host=postgresdb \
  --db_password=Pa55w0rd \
  --config=/etc/odoo/odoo.conf \
  -d test_detalex_datev_export \
  --test-enable \
  --stop-after-init \
  --without-demo=all \
  -i dtx_datev_export_xml \
  --test-tags /dtx_datev_export_xml:TestDatevExport
```

### 🐞 Mit Debugger (debugpy)
```bash
# Einzelnen Test mit Debugger
docker exec -it --user root detalex_apps_18-odoo-web-1 \
  python3 -m debugpy --listen 0.0.0.0:8889 --wait-for-client usr/bin/odoo \
  --db_host=postgresdb --db_password=Pa55w0rd \
  --config=/etc/odoo/odoo.conf -d test_detalex_datev_export \
  --test-enable --stop-after-init --without-demo=all \
  -i dtx_datev_export_xml \
  --test-tags .test_get_invoices_all_types
```

### 📁 Test-Dateien Struktur
```
dtx_datev_export_xml/
├── tests/
│   ├── __init__.py           # ⚠️ WICHTIG: Test-Dateien hier importieren!
│   └── test_datev_export.py  # Tests für DatevExport Model (✅ 39 Tests ALLE PASS)
```

**⚠️ WICHTIG - Nicht vergessen!**
Neue Test-Dateien müssen in `tests/__init__.py` importiert werden:
```python
# tests/__init__.py
from . import test_datev_export
```

### ✅ TEST RESULTS (Stand: 2025-10-15)
```bash
Module dtx_datev_export_xml: 0 failures, 0 errors of 39 tests
```

**Alle 9 neuen Tests für Dokumententyp-Filter bestanden:**
- ✅ test_01_document_type_filter_all_types_enabled
- ✅ test_02_document_type_filter_only_outgoing
- ✅ test_03_document_type_filter_only_incoming
- ✅ test_04_document_type_filter_only_invoices
- ✅ test_05_document_type_filter_none_selected_raises_error
- ✅ test_06_document_type_filter_description_shows_selected_types
- ✅ test_07_document_type_filter_checkbox_change_in_draft
- ✅ test_08_document_type_filter_default_values
- ✅ test_09_document_type_filter_write_triggers_reload
```
dtx_datev_export_xml/
├── tests/
│   ├── __init__.py           # ⚠️ WICHTIG: Test-Dateien hier importieren!
│   └── test_datev_export.py  # Tests für DatevExport Model
```

**⚠️ WICHTIG - Nicht vergessen!**
Neue Test-Dateien müssen in `tests/__init__.py` importiert werden:
```python
# tests/__init__.py
from . import test_datev_export
# Weitere Test-Dateien hier importieren
```

### 🎨 Test-Klasse Beispiel
```python
from odoo.tests import tagged, TransactionCase

@tagged('post_install', '-at_install')
class TestDatevExport(TransactionCase):
    """Tests für DatevExport Model mit Dokumententyp-Filter"""

    def test_get_invoices_all_types(self):
        """Test: Alle Dokumententypen aktiviert"""
        export = self.env["datev.export"].create({
            "date_start": "2024-01-01",
            "date_stop": "2024-12-31",
            "include_out_invoice": True,
            "include_out_refund": True,
            "include_in_invoice": True,
            "include_in_refund": True,
        })
        invoices = export.get_invoices()
        self.assertTrue(len(invoices) > 0, "Sollte Invoices finden")
```

---

## 📚 RELATED CODE LOCATIONS

### Models:
- ✅ `models/datev_export.py` → Hauptlogik
- ✅ `models/datev_zip_generator.py` → ZIP Generation (nicht geändert)
- ✅ `models/datev_xml_generator.py` → XML Generation (nicht geändert)

### Views:
- ✅ `views/datev_export_views.xml` → Formular mit Checkboxen
- ✅ `views/account_invoice_view.xml` → Account Move Extensions (nicht geändert)

### Tests:
- ⚠️ `tests/test_datev_export.py` → **9 NEUE TESTS ERSTELLT!**
  - `test_01_document_type_filter_all_types_enabled` ✅
  - `test_02_document_type_filter_only_outgoing` ✅
  - `test_03_document_type_filter_only_incoming` ✅
  - `test_04_document_type_filter_only_invoices` ✅
  - `test_05_document_type_filter_none_selected_raises_error` ✅
  - `test_06_document_type_filter_description_shows_selected_types` ✅
  - `test_07_document_type_filter_checkbox_change_in_draft` ✅
  - `test_08_document_type_filter_default_values` ✅
  - `test_09_document_type_filter_write_triggers_reload` ✅

---

## ✅ TODO LISTE

- [x] Unit Tests schreiben (9 Tests erstellt!)
- [x] Tests ausführen und validieren ✅ **ALLE 39 TESTS BESTANDEN!**
- [ ] Migration Script für bestehende Exports
- [ ] User Dokumentation aktualisieren
- [ ] Entscheidung: Checkbox-Änderung triggert Auto-Reload? (siehe `write()`)
- [ ] Performance Test mit vielen Invoices
- [ ] UI/UX Review der Checkbox-Gruppe
- [ ] XML View mit Checkbox-Group erweitern (Code bereit, muss noch eingefügt werden)

---

## 🎯 RELEASE NOTES (für User)

### Neu in Version X.X.X:

**Dokumententyp-Filter**
Sie können jetzt genau auswählen, welche Dokumententypen exportiert werden sollen:
- ✅ Ausgehende Rechnungen (Kundenrechnungen)
- ✅ Ausgehende Gutschriften (Kundengutschriften)
- ✅ Eingehende Rechnungen (Lieferantenrechnungen)
- ✅ Eingehende Gutschriften (Lieferantengutschriften)

**Standardverhalten**: Alle Typen sind aktiviert (wie bisher).

**Hinweis**: Mindestens ein Typ muss ausgewählt sein.

---

## 📞 KONTAKT BEI FRAGEN

- **Code Owner**: [Dein Name]
- **Module**: dtx_datev_export_xml
- **Odoo Version**: 18.0
- **Letzte Änderung**: 15. Oktober 2025

---

## ⚡ QUICK REFERENCE

```python
# Beispiel: Export nur für Ausgehende Rechnungen erstellen
export = env['datev.export.xml'].create({
    'date_start': '2025-01-01',
    'date_stop': '2025-12-31',
    'include_out_invoice': True,   # ✅
    'include_out_refund': False,   # ❌
    'include_in_invoice': False,   # ❌
    'include_in_refund': False,    # ❌
})
invoices = export.get_invoices()  # Nur out_invoice
```

---

**ENDE DER NOTIZEN**
