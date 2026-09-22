# 🚢 CargoVeritas — Automated Shipping Document Verification

**Averis x Monash Hackathon 2026** • **Team: AppleCat**  
🌐 **Live Platform:** [https://cargo-veritas.vercel.app](https://cargo-veritas.vercel.app)

---

CargoVeritas is an automated SaaS Control Tower that connects directly to operational mailboxes, intelligently sorts incoming shipping communications, and automatically checks customer Shipping Instructions (SI) against ocean carrier draft Bills of Lading (B/L) across 7 mandatory logistics fields in seconds. Ambiguous or unreadable documents trigger a human-in-the-loop escalation rather than making blind guesses.

---

### 📑 Table of Contents
1. [Key Features](#-key-features)
2. [Tech Stack](#-tech-stack)
3. [Prerequisites](#-prerequisites)
4. [Environment Variables](#-environment-variables)
5. [Google Cloud & Gmail Setup (Important for Evaluators)](#-google-cloud--gmail-setup-important-for-evaluators)
6. [Local Setup & Installation](#-local-setup--installation)
7. [Supabase Database & Storage Setup](#-supabase-database--storage-setup)
8. [Running the Application](#-running-the-application)
9. [Benchmark Evaluation Pipeline (`submission.json`)](#-benchmark-evaluation-pipeline-submissionjson)
10. [Simulating Verification Scenarios](#-simulating-verification-scenarios)
11. [Deployment (Vercel)](#-deployment-vercel)
12. [Team & License](#-team--license)
    
## ✨ Key Features

- **Inbox Intelligence Engine**  
  Synchronizes operational inboxes and sorts incoming communications into 5 distinct categories:  
  `BL_COMPARISON` • `SI_REQUEST` • `INVOICE_QUERY` • `GENERAL` • `SPAM`

- **Automated 7-Field Cross-Alignment**  
  Compares Shipping Instructions against draft Bills of Lading side-by-side in ~3 seconds across all critical fields:
  - Shipper & Consignee
  - Notify Party
  - Port of Loading & Port of Discharge
  - Container Count & Gross Weight (kg)

- **Deterministic Extraction (Zero Hallucination)**  
  Uses OpenAI structured JSON mode with temperature 0.0, aligning carrier-specific aliases (e.g., "Load Port" vs "Port of Loading") without schema errors.

- **Human-in-the-Loop Escalation**  
  Routes unreadable scans, missing files, or field mismatches directly to an operator queue featuring 1-click actions:  
  *Approve Discrepancy* • *Reject to Carrier* • *Request Clean Copy*

- **Audit-Ready Persistence**  
  Maintains secure attachment storage and relational verification audit logs backed by Supabase with Row-Level Security (RLS).

## 🛠️ Tech Stack

* **Frontend & Control Tower:** Next.js (App Router), React, Tailwind CSS
* **Backend & Verification API:** Python (FastAPI / Serverless handlers on Vercel)
* **Database & Document Persistence:** Supabase (PostgreSQL, Object Storage, Row-Level Security)
* **Extraction Engine:** OpenAI API (`gpt-4o` / `gpt-4o-mini` with strict structured JSON mode)
* **Document Parsing & OCR:** PyMuPDF (`fitz`), RapidOCR, `pypdf`, `python-docx`, `openpyxl`
* **Prompt Engineering:** Google Gemini
* **Cloud & Mailbox Ingestion:** Google Cloud Console (Gmail API, OAuth 2.0), Vercel

---

## 📋 Prerequisites

Ensure you have the following installed and configured before running locally:

* **Node.js:** Version 18.17.0 or higher ([Download Node.js](https://nodejs.org/en))
* **Python:** Version 3.10 or higher ([Download Python](https://www.python.org/downloads/))
* **Package Manager:** `npm` (bundled with Node), `pnpm`, or `yarn`
* **Supabase Account:** Free account at [supabase.com](https://supabase.com/)
* **OpenAI API Key:** Active API key from [platform.openai.com](https://platform.openai.com/home)
* **Google Cloud Console:** Active project on [console.cloud.google.com](https://console.cloud.google.com/) with Gmail API enabled

---

## 🔐 Environment Variables

Create a `.env.local` file in the root directory of your project:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# OpenAI API Configuration
OPENAI_API_KEY=sk-your-openai-api-key

# Google Cloud / Gmail OAuth 2.0
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=https://cargo-veritas.vercel.app/auth/gmail/callback

# App Base URL
NEXT_PUBLIC_APP_URL=https://cargo-veritas.vercel.app
```

> [!WARNING]
> **Security Notice:** Never commit `.env.local` or private API keys to your public repository. Ensure `.env.local` is listed in `.gitignore`.

---

## ⚠️ Google Cloud & Gmail Setup (Important for Evaluators)

### 📌 Sandbox Mode Notice
Because Google OAuth is currently in **Testing Mode**, Google requires any external Gmail account to be whitelisted before connecting to the live inbox sync.

* **Testing on Live App:** Reach out to Team AppleCat with your Gmail address. We will whitelist your account in Google Cloud Console (`OAuth consent screen` → `Test users`) so you can link your mailbox without hitting `Error 403: access_denied`.
* *Note:* You can fully evaluate the platform without syncing live Gmail by using the pre-seeded simulation records in the dashboard.

---

### 💻 If Setting Up Your Own Local Instance

1. In the [Google Cloud Console](https://console.cloud.google.com/), create a project (e.g., `cargoveritas-dev`).
2. Go to **APIs & Services → Library**, search for **Gmail API**, and click **Enable**.
3. Go to **APIs & Services → OAuth consent screen**:
   - Choose **External** and enter app details.
   - Add scope: `https://www.googleapis.com/auth/gmail.readonly`.
   - Under **Test users**, add your own Gmail address.
4. Go to **APIs & Services → Credentials → Create Credentials → OAuth client ID**:
   - **Application type:** Web application
   - **Authorised JavaScript origins:**  
     `https://cargo-veritas.vercel.app` (or `http://localhost:3000` for local dev)
   - **Authorised redirect URIs:**  
     `https://cargo-veritas.vercel.app/auth/gmail/callback` (or `http://localhost:3000/auth/gmail/callback` for local dev)
5. Copy your **Client ID** and **Client Secret** into your `.env.local`.

## 🚀 Local Setup & Installation

### 1. Clone the Repository
```
git clone https://github.com/your-username/cargo-veritas.git
cd cargo-veritas
```

### 2. Install Dependencies
Using npm:
```
npm install
```
Or using pnpm:
```
pnpm install
```

**🗄 Supabase Database & Storage Setup**
**1. Database Schema** <br />
In your Supabase project dashboard, navigate to the SQL Editor and run the following script:
```
-- Enable UUID extension
create extension if not exists "uuid-ossp";
-- Table: Shipments / Verifications
create table public.verifications (
  id uuid default uuid_generate_v4() primary key,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  user_id uuid references auth.users(id) on delete set null,
  email_subject text,
  email_sender text,
  email_category text default 'BL_CHECK',
  status text default 'PENDING', -- 'PASSED', 'MISMATCH', 'UNREADABLE', 'APPROVED', 'REJECTED'
  shipper_match boolean default false,
  consignee_match boolean default false,
  notify_party_match boolean default false,
  pol_match boolean default false,
  pod_match boolean default false,
  container_count_match boolean default false,
  gross_weight_match boolean default false,
  si_data jsonb,
  bl_data jsonb,
  discrepancies jsonb,
  rejection_notes text
);

-- Enable Row Level Security (RLS)
alter table public.verifications enable row level security;

-- Policy: Allow authenticated users to view and update verifications
create policy "Allow authenticated read" on public.verifications
  for select using (auth.role() = 'authenticated');

create policy "Allow authenticated insert/update" on public.verifications
  for all using (auth.role() = 'authenticated');
```

**2. Storage Buckets** <br />
1. In the Supabase Dashboard, go to Storage > New Bucket.
2. Create a bucket named shipping-documents.
3. Toggle on Public bucket (or set appropriate RLS policies for authenticated access).
4. This bucket stores customer SI PDFs and carrier draft B/L attachments.

**💻 Running the Application**
Start Development Server
```
npm run dev
```
Open your browser and navigate to:
```
http://localhost:3000
```
Production Build Test
To verify production readiness locally:
```
npm run build
npm start
```

**🧪 Simulating Verification Scenarios** <br />
You can test the live comparison engine using the two baseline scenarios demonstrated during the hackathon: <br />

**Scenario 1: Clean Pass (Auto-Cleared)** <br />
**Input:** Shipping Instructions matching carrier Draft B/L (matching Shipper, Consignee, Notify Party, Load Port, Discharge Port, Container Count, and Gross Weight). <br />
**Result:** System extracts all 7 fields in ~3 seconds, displays green checks across all fields, and commits the result directly to Supabase with status PASSED. <br />

**Scenario 2: Gross Weight Discrepancy (Human Review)** <br />
**Input:** Shipping Instructions stating 24,500 KG while Carrier Draft B/L reads 21,000 KG. <br />
**Result:** System matches companies and ports, highlights the Gross Weight mismatch in red, flags the discrepancy, and queues the record into the Human-in-the-Loop review queue for 1-click Reject to Carrier action. <br />

**🌐 Deployment (Vercel)** <br />
The easiest way to deploy this repository is using Vercel: <br />
1. Push your code to your GitHub repository.
2. In the Vercel dashboard, click "New Project" and import your cargo-veritas repository.
3. Configure your Environment Variables in Vercel (NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, OPENAI_API_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI).
4. Click Deploy. Vercel will trigger CI/CD builds on every git push.

**👥 Team AppleCat** <br />
Built for the Averis x Monash Hackathon 2026. <br />
Project: CargoVeritas <br />
Live Demo: Visit [cargo-veritas.vercel.app] (https://cargo-veritas.vercel.app) and click Sign Up to create an account and access the control tower. <br />
Feedback & Questions: Open an issue in this repository.
