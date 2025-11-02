# odoo-datev-xml-export

[![Odoo Version](https://img.shields.io/badge/Odoo-18.0-blue.svg)](https://github.com/odoo/odoo)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)

German DATEV XML Export module for Odoo 18.0 - Advanced accounting integration with German DATEV system.

## 📋 Overview

This repository contains comprehensive Odoo modules for exporting invoices, bills, and digitized receipts to the German **DATEV** accounting system using the modern **XML interface format**.

**⚠️ Proprietary Software** - This repository contains proprietary code from Detalex GmbH. For detailed functionality, licensing information, and configuration guides, see the module documentation.

---

## 🎯 Main Modules

### 📦 dtx_datev_export_xml
**Primary module for DATEV XML export**

Complete DATEV XML export functionality with support for:
- ✅ Invoice exports (Ausgangsrechnungen)
- ✅ Bill exports (Eingangsrechnungen) 
- ✅ Credit/Debit notes (Gutschriften/Lastschriften)
- ✅ Digitized receipt attachments (PDF)
- ✅ Batch export & export tracking
- ✅ DATEV validation & error handling
- ✅ Magic Button for validation error correction

**📖 Full Documentation:** See [`dtx_datev_export_xml/README.md`](./dtx_datev_export_xml/README.md)

---

### 🛠️ dtx_datev_export
**Base DATEV export functionality**

Foundation module providing:
- Core export configuration
- DATEV format support
- Company settings integration
- Basic export workflows

**📖 Full Documentation:** See [`dtx_datev_export/README.md`](./dtx_datev_export/README.md)

---

## 🚀 Quick Start

### Installation

1. **Clone the repository** into your Odoo addons directory:
   ```bash
   git clone -b 18.0 https://github.com/Detalex-GmbH/odoo-datev-xml-export.git
   cd odoo-datev-xml-export
   ```

2. **Install the modules** in Odoo:
   - Go to `Apps` → `Update Apps List`
   - Search for `DATEV`
   - Click `Install` on `DATEV XML Export` module

3. **Configure** in Odoo:
   - Go to `Settings` → `Companies` → select your company
   - Configure DATEV export settings
   - Set up company information for DATEV exports

### Basic Usage

1. **Navigate** to `Accounting` → `DATEV Export`
2. **Create Export** or use the `Magic Button` on invoices
3. **Review** export data
4. **Download** the XML file
5. **Import** into DATEV system

For detailed usage instructions, see the module documentation.

---

## 📋 Requirements

- **Odoo:** 18.0+
- **Python:** 3.11+
- **Database:** PostgreSQL 12+
- **Modules:** 
  - `account` (core Accounting module)
  - `base` (Odoo core)
  - `website` (optional, for web export features)

---

## 🔧 Configuration

### Company Settings

Access configuration at: `Settings` → `Companies` → Select Company → DATEV Export Settings

Key configuration fields:
- **DATEV Konto** - DATEV account number
- **Consultant Number** - DATEV consultant identification
- **Client Number** - DATEV client identification  
- **Export Format** - Select XML export format
- **Receipt Storage** - Configure digital receipt handling

### Advanced Settings

For advanced configuration options and system settings, see:
- [`dtx_datev_export_xml/readme/CONFIGURATION.rst`](./dtx_datev_export_xml/readme/CONFIGURATION.rst)

---

## 📚 Documentation

### For Users
- **Quick Start Guide:** This README
- **Module Documentation:** [`dtx_datev_export_xml/README.md`](./dtx_datev_export_xml/README.md)
- **Configuration Guide:** [`dtx_datev_export_xml/readme/CONFIGURATION.rst`](./dtx_datev_export_xml/readme/CONFIGURATION.rst)
- **Usage Guide:** [`dtx_datev_export_xml/readme/USAGE.rst`](./dtx_datev_export_xml/readme/USAGE.rst)

### For Developers
- **Module Structure:** See module directories
- **API Documentation:** Inline code documentation
- **Contributing:** See CONTRIBUTING.md (if applicable)

---

## 🐛 Features & Capabilities

### Core Features
- ✅ **XML Export Format** - Modern DATEV XML interface (v6.2+)
- ✅ **Multi-Document Type** - Invoices, Bills, Credit Notes, Debit Notes
- ✅ **Batch Processing** - Export multiple documents in one operation
- ✅ **Export Tracking** - Complete export history with timestamps
- ✅ **Error Handling** - Validation and error reporting
- ✅ **Digital Receipts** - Automatic PDF attachment handling

### Advanced Features
- 🔮 **Magic Button** - One-click DATEV validation error correction
- 🎯 **Smart Filtering** - Filter exports by date, partner, or document type
- 📊 **Export Statistics** - Track export volume and success rates
- 🔐 **Permission Management** - Role-based export access control
- 🌍 **Multi-Company Support** - Support for multiple company configurations

---

## 📂 Directory Structure

```
odoo-datev-xml-export/
├── dtx_datev_export_xml/          # Main XML export module
│   ├── models/                    # Data models & business logic
│   ├── views/                     # UI forms and views
│   ├── static/                    # CSS, JS, images
│   ├── xsd_files/                 # DATEV XSD schema files
│   ├── readme/                    # Detailed documentation
│   ├── __manifest__.py            # Module metadata
│   └── README.md                  # Module documentation
│
├── dtx_datev_export/              # Base export module
│   ├── models/                    # Core models
│   ├── views/                     # Base views
│   ├── static/                    # Resources
│   ├── musterdaten/               # Sample data
│   ├── __manifest__.py
│   └── README.md
│
└── README.md                      # This file
```

---

## 🔐 Security & Privacy

- **Proprietary Code** - This repository contains proprietary code from Detalex GmbH
- **License** - See LICENSE file for licensing terms
- **Data Security** - DATEV export handles sensitive financial data
- **GDPR Compliant** - Respects data privacy regulations

---

## 🆘 Support & Issues

### Getting Help

For support, please contact:
- **Email:** support@detalex.de
- **Website:** https://detalex.de
- **Documentation:** See module README files

### Reporting Issues

Before reporting issues, please:
1. Check the module documentation
2. Review the configuration guide
3. Check existing GitHub issues
4. Provide detailed error messages and logs

---

## 📝 License

This repository contains **proprietary code** owned by Detalex GmbH.

- **License Type:** Other Proprietary (see LICENSE file)
- **Copyright:** © 2025 Detalex GmbH
- **Usage:** Limited to licensed users only

For licensing inquiries, contact: info@detalex.de

---

## 👥 Authors & Contributors

**Primary Developer:** Dietmar Hamm (hamm@detalex.de)  
**Company:** Detalex GmbH  
**Website:** https://detalex.de

---

## 📅 Changelog

### Version 18.0 (2025-11-02)
- ✨ Full Odoo 18.0 compatibility
- 🎨 Modernized UI following Odoo 18 standards
- ⚡ Performance improvements
- 🔧 Enhanced Magic Button functionality
- 📦 Initial public release on GitHub

For detailed changelog, see module documentation.

---

## 🔗 Related Links

- **DATEV Official:** https://www.datev.de/
- **Odoo Documentation:** https://www.odoo.com/documentation/
- **German Tax Authority:** https://www.bzbservices.de/

---

## ⭐ Support

If you find this module useful, please consider:
- ⭐ Starring this repository
- 🐛 Reporting issues
- 💬 Providing feedback
- 🤝 Contributing improvements

---

**Last Updated:** November 2, 2025  
**Repository Status:** Active  
**Odoo Version:** 18.0+  
**Python Version:** 3.11+

---

## 📞 Contact

**Detalex GmbH**  
Website: https://detalex.de  
Email: info@detalex.de  
Support: support@detalex.de

---

**Disclaimer:** This is a proprietary module. Unauthorized distribution, modification, or use is prohibited. See LICENSE file for details.
