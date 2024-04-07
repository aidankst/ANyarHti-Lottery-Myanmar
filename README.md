# A Nyar Hti - Lottery

**by**: Kaung Sithu

## Overview

This project aims to help A Nyar Hti - Lottery, helping Myanmar's Spring Revolution. A Nyar Hti is supporting PDFs in funding and other factors. This Flask application facilitates the selling and management of lottery tickets, integrated with Firebase for authentication and data storage.

## Dependencies

* Python 3+
* Flask
* Firebase (pyrebase)
* Pillow (PIL)
* QRCode (qrcode)
* smtplib

## Setup

**Firebase Configuration:**
   * Create a Firebase project.
   * Enable Email/Password Authentication in the Firebase console.
   * Create a Realtime Database.
   * Update `firebaseConfig.py` (or similar) with your Firebase project details.



## Features

**User Authentication**:
- User registration.
- User login.
- Password reset.
- Email verification.
  
**Lottery Ticket Selling**:
- Form to apply for lottery tickets.
- Generate random or user-specified ticket numbers. The server will check for existing ticket numbers and if it is new, it will continue next step.
- Store ticket information in Firebase database.

**Lottery Ticket Generation**:
- Customize a ticket template.
- Embed ticket information (Ticket Number, Lottery Sequence, Buyer Name, Seller Name) and a QR code (with necessary information) on the ticket.
- Save generated tickets as PNG images.

**Email Tickets to Buyers**

**Admin Panel (Basic)**

## Disclaimer

This project is intended for demonstration purposes.
