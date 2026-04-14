==================
DATEV XML Export
==================

This addon provides advanced functionality for exporting invoices and bills to the German DATEV system
using the modern XML interface format with digitized receipt support.

Features
========

1. Complete DATEV XML export for invoices and bills
2. Digitized receipt attachment handling
3. Time-based and individual export capabilities
4. Magic buttons for exported invoice navigation
5. DATEV validation with error handling
6. Automatic PDF merging for multiple attachments
7. Comprehensive export tracking and monitoring
8. Integration with DATEV Unternehmen Online
9. Document type filters (NEW in 17.0.2.0)

DATEV XML interface provides structured accounting data transfer and is the modern
replacement for ASCII-based exports, offering better validation and receipt handling.

Technical Details
=================

- Extends account.move with DATEV XML export functionality
- Provides datev.export.xml model for export management
- XML/ZIP generation with XSD validation
- PDF processing and attachment handling
- Export state tracking and error management
- Magic button integration for UX enhancement
- Document type filtering (customer/vendor invoices/refunds)

Limitations
===========

- Does not support pure G/L account postings
- No master data transfer for business partners
- Certain §13b UStG cases require manual handling

Version History
===============

- **17.0.1.3**: Added UI help block for export_bu_code field with warnings and documentation link
- **17.0.1.2**: Fixed GitHub documentation links to point to public repository
- **17.0.1.1**: Added export_bu_code field for optional BU-Code (Buchungsschlüssel) export control
  with comprehensive documentation and steuerberater workflow integration
- **17.0.1.0**: Unified version with magic button validation features, comprehensive documentation
- **17.0.0.13**: Magic Button for DATEV validation errors with animation and group restrictions
- **17.0.0.12**: Refactoring of datev_cost_category, improved test coverage
- **17.0.0.11**: Removed datev_export_state field and related references
- **17.0.0.10**: Cleaned up posting text and short description of invoice lines
- **17.0.0.9**: Bug fixes in tests and translations
- **17.0.0.8**: Adjustments to datev_exported field and pluralization
- **17.0.0.7**: Bug fix in tests with new PDF merging logic
- **17.0.0.6**: Multiple PDF attachments merged, renamed customer/vendor exports
- **17.0.0.5**: Added XML validation before export
- **17.0.0.4**: Added DATEV XML export menu to accountant menu
- **17.0.0.3**: Moved DATEV XML export menu to Apps menu
- **17.0.0.2**: Bug fix in invoices Smart Button
- **17.0.0.1**: Added DATEV XML export menu to main menu
- **17.0.0.0**: Migration to Odoo 17
