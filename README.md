# 📧 Send Mail

> **A secure, personalized cold email automation platform built with Django that enables businesses to create, manage, and monitor email campaigns directly from their own Gmail accounts.**




\

---

# 📚 Table of Contents

* [About the Project](#-about-the-project)
* [Business Domain](#-business-domain)
* [Key Features](#-key-features)
* [Technology Stack](#-technology-stack)
* [Project Architecture](#-project-architecture)
* [Project Workflow](#-project-workflow)
* [Project Structure](#-project-structure)
* [Application Routes](#-application-routes)
* [Authentication Flow](#-authentication-flow)
* [Security Features](#-security-features)
* [License](#-license)

---

# 📖 About the Project

Send Mail is a secure cold-email automation platform designed for:

* 📈 Marketing Teams
* 💼 Sales Professionals
* 🚀 Startup Founders
* 🏢 Small & Medium Businesses

The platform enables users to securely connect their Gmail accounts using **Google App Passwords**, upload recipient lists from CSV/Excel files, send personalized email campaigns in background batches, and automatically track incoming replies through IMAP.

Unlike traditional email marketing tools, Send Mail gives users complete control over their own email infrastructure while maintaining security through encrypted credential storage.

---

# 🏢 Business Domain

Send Mail belongs to the **Sales & Marketing Automation** domain.

Its primary purpose is to automate personalized cold outreach campaigns while providing:

* Secure Gmail integration
* Personalized email generation
* Bulk email scheduling
* Reply tracking
* Campaign analytics
* Contact suppression management

---

# ✨ Key Features

## 🔐 Secure Authentication

* User Registration
* Login
* Gmail App Password Verification
* Email OTP Verification
* Secure Django Sessions

---

## 🔒 Encrypted Credential Storage

User Gmail App Passwords are:

* Verified before account creation
* Encrypted using **Fernet (AES)**
* Never stored in plaintext
* Decrypted only when sending emails

---

## 📁 CSV & Excel Upload

Supports:

* CSV (.csv)
* Excel (.xlsx)

Features:

* Automatic validation
* Required column checking
* Bulk recipient import
* Duplicate prevention
* Suppression list filtering

---

## ✉ Personalized Email Campaigns

Every email can be personalized using recipient information.

Example:

```
Hi John,

Thank you for your interest...
```

instead of

```
Hi,
```

---

## ⚙ Background Email Sending

Campaigns are processed asynchronously using:

* Python Threading
* Django Management Commands
* Cron Jobs

Features include:

* Batch sending
* Configurable delays
* SMTP rate-limit protection
* Daily sending limits

---

## 📥 Reply Tracking

Integrated IMAP functionality allows users to:

* Fetch replies
* Read conversations
* Reply directly
* Store responses inside Send Mail

---

## 🚫 Suppression List

Prevent accidental emails by maintaining:

* Unsubscribed contacts
* Bounced emails
* Blocked recipients

---

## 📱 Responsive Dashboard

Built using Django Templates and Bootstrap 5.

Features:

* Campaign Dashboard
* Status Badges
* Email Preview
* Reply Modal
* Flash Messages
* Sticky Footer
* Mobile Responsive Layout

---

# 🛠 Technology Stack

## Backend

| Technology            | Purpose                |
| --------------------- | ---------------------- |
| Python 3.x            | Backend Language       |
| Django 6.0            | Web Framework          |
| Django ORM            | Database ORM           |
| SQLite                | Development Database   |
| Pandas                | CSV & Excel Processing |
| Openpyxl              | Excel Parsing          |
| Cryptography (Fernet) | Password Encryption    |
| IMAPClient            | Reply Fetching         |
| Python-dotenv         | Environment Variables  |
| smtplib               | Email Sending          |
| threading             | Background Processing  |

---

## Frontend

| Technology       | Purpose               |
| ---------------- | --------------------- |
| Django Templates | Server-Side Rendering |
| Bootstrap 5.3    | Responsive UI         |
| HTML5            | Structure             |
| CSS3             | Styling               |
| JavaScript       | Client Interactions   |

---

# 🏗 Project Architecture

Send Mail follows a **Monolithic Django MVT (Model-View-Template)** architecture.

```
Browser
    │
HTTP Request
    │
    ▼
Django Views
    │
 ┌──┴───────────────┐
 │                  │
Models          Templates
 │                  │
 └──────────────┬───┘
                │
           SQLite Database
```

Background tasks are handled using Python Threading and Django Management Commands.

---

# 🔄 Project Workflow

```
User Registration
        │
        ▼
SMTP Authentication
        │
        ▼
Email OTP Verification
        │
        ▼
Encrypted Credential Storage
        │
        ▼
Upload CSV/XLSX
        │
        ▼
Recipient Processing
        │
        ▼
Background Email Sending
        │
        ▼
IMAP Reply Tracking
```

---

# 📁 Project Structure

```
CampaignManager
│
├── email_system/
│
├── accounts/
│
├── campaigns/
│   ├── management/
│   ├── services.py
│   ├── security.py
│   ├── forms.py
│   ├── models.py
│   └── views.py
│
├── footer/
│
├── templates/
│
├── static/
│
├── media/
│
├── manage.py
│
└── requirements.txt
```

---

# 🌐 Application Routes

| URL                             | Method   | Description        | Auth |
| ------------------------------- | -------- | ------------------ | ---- |
| `/accounts/register/`           | GET/POST | User Registration  | ❌    |
| `/accounts/verify-otp/`         | GET/POST | OTP Verification   | ❌    |
| `/accounts/login/`              | GET/POST | User Login         | ❌    |
| `/`                             | GET/POST | Dashboard          | ✅    |
| `/campaign/<pk>/`               | GET      | Campaign Details   | ✅    |
| `/campaign/<pk>/send/`          | POST     | Start Campaign     | ✅    |
| `/campaign/<pk>/check-replies/` | POST     | Fetch Replies      | ✅    |
| `/recipient/<id>/reply/`        | POST     | Reply to Recipient | ✅    |

---

# 🔐 Authentication Flow

1. User registers using Gmail and App Password.
2. SMTP credentials are verified immediately.
3. A 6-digit OTP is sent to the user's email.
4. OTP verification creates the account.
5. Gmail App Password is encrypted using Fernet.
6. Django creates a secure session.
7. Protected routes use `@login_required`.

---

# 🛡 Security Features

* Gmail App Password Encryption (Fernet AES)
* OTP Email Verification
* Atomic Database Transactions
* Secure Session Authentication
* HTML Sanitization
* File Type Validation
* File Size Validation
* Upload Limits
* Suppression List Protection
* Production Security Headers
* CSRF Protection
* Secure Cookies
* HSTS Support

---

## ⭐ Support

If you found this project useful, please consider giving it a ⭐ on GitHub.

Your support helps improve the project and encourages future development.

---

**Built with ❤️ using Django, Bootstrap, Pandas, IMAPClient, and Cryptography.**
