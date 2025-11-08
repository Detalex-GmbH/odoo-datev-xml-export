# DATEV Export Base

**Version:** 18.0.1.2
**Kategorie:** Accounting/Localizations
**Autor:** Detalex GmbH, Dietmar Hamm (hamm@detalex.de)
**Website:** https://detalex.de
**Lizenz:** Other proprietary

## Beschreibung

Das **DATEV Export Base** Addon stellt die Grundfunktionalität für den Export von Buchhaltungsdaten in das deutsche DATEV-System bereit. DATEV ist eine weit verbreitete Buchhaltungssoftware in Deutschland, und dieses Modul bildet die Basis für verschiedene DATEV-Export-Funktionalitäten, die für die deutsche Lokalisierung erforderlich sind.

**Neu in Version 18.0:** Vollständige Kompatibilität mit Odoo 18.0, verbesserte Performance und erweiterte Integrationsmöglichkeiten für moderne DATEV-Schnittstellen.

## Features

### 1. DATEV Konfiguration
- **Berater-Nummer (Consultant Number)**: Konfiguration der DATEV Beraternummer (1000-9999999)
- **Mandanten-Nummer (Client Number)**: Konfiguration der DATEV Mandantennummer (0-99999)
- Unternehmensspezifische Einstellungen über die Accounting-Konfiguration

### 2. Technische Erweiterungen
- **res.company Erweiterung**: Fügt DATEV-spezifische Felder hinzu
  - `l10n_de_datev_consultant_number`: Beraternummer
  - `l10n_de_datev_client_number`: Mandantennummer

- **res.config.settings Erweiterung**: Einfache Konfiguration über die Einstellungen
  - Direkte Bearbeitung der DATEV-Nummern
  - Unternehmensspezifische Konfiguration

- **account.move.line Erweiterung**: DATEV-spezifische Steuerbehandlung
  - `datev_vorsteuer_automatic`: Automatische Vorsteuer-Erkennung
  - Intelligente Unterscheidung zwischen Ein- und Ausgangsrechnungen
  - Automatische Steuer-Kategorisierung

### 3. Steuer-Automatisierung
- **Ausgangsrechnungen**: Automatische Erkennung von Umsatzsteuer
- **Eingangsrechnungen**: Automatische Erkennung von Vorsteuer
- Kontextabhängige Steuerbehandlung basierend auf Rechnungstyp

## Installation

1. **Systemvoraussetzungen:**
   - Odoo Version 18.0 oder höher
   - Python 3.10+
   - PostgreSQL 13+

2. **Abhängigkeiten prüfen:**
   Stellen Sie sicher, dass die folgenden Module installiert sind:
   - `base` (Odoo Core)
   - `account` (Buchhaltungsmodul)
   - `l10n_de` (Deutsche Lokalisierung für Odoo 18.0)

3. **Modul installieren:**
   - Installieren Sie das Modul über die App-Verwaltung von Odoo
   - Oder verwenden Sie die Kommandozeile: `odoo -i dtx_datev_export`

4. **Datenbank-Migration:**
   Bei Update von älteren Versionen wird automatisch eine Datenmigration durchgeführt

## Konfiguration

### DATEV-Nummern einrichten

1. Navigieren Sie zu **Einstellungen** → **Buchhaltung**
2. Scrollen Sie zum Abschnitt **DATEV Export**
3. Tragen Sie folgende Daten ein:
   - **Berater-Nummer**: Ihre DATEV Beraternummer (1000-9999999)
   - **Mandanten-Nummer**: Ihre DATEV Mandantennummer (0-99999)

### Multi-Company Setup

Das Modul unterstützt Multi-Company-Umgebungen:
- Jedes Unternehmen kann eigene DATEV-Nummern haben
- Einstellungen sind unternehmensspezifisch
- Konfiguration pro Unternehmen in den Einstellungen

## Technische Details

### Modell-Erweiterungen

#### ResCompany
```python
class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_de_datev_consultant_number = fields.Char(company_dependent=True)
    l10n_de_datev_client_number = fields.Char(company_dependent=True)
```

#### AccountMoveLine
```python
class AccountAccount(models.Model):
    _inherit = "account.move.line"

    datev_vorsteuer_automatic = fields.Boolean(
        compute="_compute_datev_vorsteuer_automatic"
    )
```

### Views
- **res_config_settings_views.xml**: Konfigurationsformular für DATEV-Einstellungen

### Datenstrukturen
- **i18n/**: Übersetzungsdateien für Mehrsprachigkeit
- **musterdaten/**: Beispieldaten für DATEV-Konfiguration
- **static/**: Statische Dateien (Icons, CSS)

## Abhängigkeiten

- **base**: Odoo Basis-Modul
- **account**: Buchhaltungsmodul
- **l10n_de**: Deutsche Lokalisierung

## Verwendung

Dieses Modul stellt eine Basis für andere DATEV-Export-Module bereit. Es kann als Abhängigkeit für spezifische DATEV-Export-Funktionalitäten verwendet werden:

- DATEV ASCII Export
- DATEV XML Export
- DATEV Steuer-Export
- DATEV Konten-Export

## Entwickler-Hinweise

### Erweiterung des Moduls

Um dieses Basis-Modul zu erweitern:

1. Fügen Sie `dtx_datev_export` zu Ihren Abhängigkeiten hinzu
2. Nutzen Sie die bereitgestellten DATEV-Felder in `res.company`
3. Erweitern Sie die `account.move.line` Logik nach Bedarf

### API-Nutzung

```python
# Zugriff auf DATEV-Konfiguration
company = self.env.company
consultant_number = company.l10n_de_datev_consultant_number
client_number = company.l10n_de_datev_client_number

# Steuer-Automatisierung prüfen
move_line = self.env['account.move.line'].browse(line_id)
is_automatic_vat = move_line.datev_vorsteuer_automatic
```

## Support

Für Support und weitere Informationen kontaktieren Sie:
- **Email**: hamm@detalex.de
- **Website**: https://detalex.de

## Changelog

### Version 18.0.1.2
- **🎨 UI Verbesserungen**: Optimierte Hilfe-Texte und Formular-Darstellung
- **📚 Erweiterte Inline-Dokumentation**: Bessere Erklärungen direkt in der Benutzeroberfläche
- **✨ UX-Optimierung**: Verbesserte Benutzerführung bei BU-Code Konfiguration

### Version 18.0.1.1
- **📝 BU-Code Feld**: Neues `l10n_de_datev_code` Feld für DATEV Buchungsschlüssel auf Steuern
- **📚 Umfassende Dokumentation**: Ausführliche Hilfe-Texte und dedizierte README_BU_CODE.md
- **🔗 GitHub Link Korrektur**: Alle Dokumentationslinks auf öffentliches Repository aktualisiert
- **🎨 UI Erweiterung**: Formular-View für BU-Code Pflege mit kontextbezogenen Hilfe-Texten
- **🌍 Übersetzungen**: Deutsche Übersetzungen für alle neuen Felder und Texte

### Version 18.0.1.0
- **Odoo 18.0 Kompatibilität**: Vollständige Anpassung an Odoo Version 18.0
- **Verbesserte Performance**: Optimierte Datenbankabfragen und Berechnungen
- **Enhanced Multi-Company**: Erweiterte Multi-Unternehmen-Funktionalität
- **Modernisierte UI**: Aktualisierte Benutzeroberfläche entsprechend Odoo 18.0 Standards
- **Sicherheits-Updates**: Aktuelle Sicherheitsstandards und Best Practices
- **API-Erweiterungen**: Neue REST-API Endpunkte für externe Integrationen
- **Erweiterte Logging**: Verbesserte Protokollierung und Fehlerbehandlung
- **Deutsche Lokalisierung 18.0**: Anpassung an die neueste deutsche Lokalisierung
- **DATEV-Standard Updates**: Unterstützung neuester DATEV-Schnittstellen-Standards

### Version 17.0.1.0 (Legacy)
- Initiale Version mit DATEV-Basis-Funktionalität
- DATEV Berater- und Mandantennummer-Konfiguration
- Automatische Steuer-Erkennung für Rechnungen
- Multi-Company-Unterstützung
- Deutsche Lokalisierung Integration
