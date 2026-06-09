# QR Code Generator

A desktop QR code generator built with Python and Tkinter. Supports multiple QR types, visual customization, and image export — no internet connection required after installation.

---

## Requirements

- Python 3.8 or higher
- pip

---

## Installation

Install the required dependencies with a single command:

```bash
pip install qrcode[pil] pillow
```

---

## Running the Application

```bash
python qr.py
```

The GUI window will open immediately. No configuration or setup is needed.

---

## Features

### QR Code Types

The application supports six QR content types. Selecting a type from the dropdown updates the form fields accordingly.

**Text / URL**
Encodes any plain text or web address. Suitable for website links, short messages, or any arbitrary string.

**E-mail**
Generates a `mailto:` URI. Fills in the recipient address, subject line, and message body. When scanned, the device's default mail client opens with the fields pre-filled.

**Phone**
Generates a `tel:` URI. When scanned on a mobile device, the dialer opens with the number ready to call.

**SMS**
Generates an `sms:` URI with an optional pre-filled message body. When scanned, the messaging app opens with the recipient and message ready.

**WiFi**
Encodes network credentials in the standard `WIFI:` format recognised by Android and iOS. Supports WPA, WEP, and open networks. When scanned, the device prompts to join the network automatically.

**vCard (Business Card)**
Generates a vCard 3.0 string containing name, phone, e-mail, organisation, and website. When scanned, the device offers to save the contact directly to the address book.

---

### Customisation Options

**Size**
A slider controls the output image size from 150 px to 600 px. The preview canvas updates to reflect the selected size.

**Error Correction**
Four levels are available. Higher levels allow the QR code to remain scannable even if part of it is damaged or obscured, at the cost of a denser pattern.

| Level | Label | Recovery Capacity |
|-------|-------|-------------------|
| L | Low | ~7% |
| M | Medium (default) | ~15% |
| Q | High | ~25% |
| H | Maximum | ~30% |

**Module Style**
Controls the shape of the individual dots that make up the QR code.

- Square — standard filled squares (maximum compatibility)
- Rounded Corner — squares with softened corners
- Circle — circular dots
- Gapped Square — squares with small gaps between them

**Colors**
Two color pickers are provided — one for the QR modules (foreground) and one for the background. Clicking either button opens the system color chooser. Any combination of colors is accepted, though sufficient contrast is required for reliable scanning.

---

### Actions

**Generate**
Reads the current form fields, builds the QR content string, applies the selected settings, and renders the result in the preview canvas. Also available via the form directly.

**Save**
Opens a file dialog to save the generated QR code image. Supported formats: PNG, JPEG, BMP. The default format is PNG.

**Clear**
Resets all form fields, sliders, color selections, and the preview canvas back to their default state.

---

## Project Structure

```
pythonqr/
    qr.py    # Main application — single file, no additional modules
    README.md
```

---

## Dependencies

| Package | Purpose |
|---------|---------|
| qrcode[pil] | QR code generation and styled rendering |
| Pillow | Image processing, color manipulation, and file export |

Tkinter is included with the standard Python distribution and does not require a separate install.

---

## Notes

- All processing is done locally. No data is sent to any external service.
- The preview scales down to fit the window if the selected size exceeds 360 px; the saved file is always at the full selected resolution.
- For WiFi QR codes, WPA2 networks should be set to the WPA option.
- vCard fields other than the name are optional and can be left blank.
