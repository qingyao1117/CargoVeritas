# 🚢 CargoVeritas — Automated Shipping Document Verification

**Averis x Monash Hackathon 2026** • **Team: AppleCat**  
🌐 **Live Platform:** [https://cargo-veritas.vercel.app](https://cargo-veritas.vercel.app)

---

CargoVeritas is an automated SaaS Control Tower that connects directly to operational mailboxes, intelligently sorts incoming shipping communications, and automatically checks customer Shipping Instructions (SI) against ocean carrier draft Bills of Lading (B/L) across 7 mandatory logistics fields in seconds. Ambiguous or unreadable documents trigger a human-in-the-loop escalation rather than making blind guesses.

---

### 📑 Table of Contents

1. [Key Features](#-key-features)
2. [Tech Stack](#️-tech-stack)
3. [Prerequisites](#-prerequisites)
4. [Environment Variables](#-environment-variables)
5. [Google Cloud & Gmail Setup (Important for Evaluators)](#-google-cloud--gmail-setup-important-for-evaluators)
6. [Local Setup & Installation](#-local-setup--installation)
7. [Supabase Database & Storage Setup](#️-supabase-database--storage-setup)
8. [Running the Application](#-running-the-application)
9. [Benchmark Evaluation Pipeline (submission.json)](#-benchmark-evaluation-pipeline-submissionjson)
10. [Simulating Verification Scenarios](#-simulating-verification-scenarios)
11. [Deployment (Vercel)](#-deployment-vercel)
12. [Team & License](#-team--license)

---

## ✨ Key Features

- **Inbox Intelligence Engine**  
  Synchronizes operational inboxes and categorizes incoming messages into 5 clear buckets:  
  `BL_COMPARISON` • `SI_REQUEST` • `INVOICE_QUERY` • `GENERAL` • `SPAM`

- **Automated 7-Field Cross-Alignment**  
  Compares Shipping Instructions against carrier draft Bills of Lading side-by-side in ~3 seconds across all mandatory fields:
  - Shipper & Consignee
  - Notify Party
  - Port of Loading & Port of Discharge
  - Container Count & Gross Weight (kg)

- **Deterministic Extraction (Zero Hallucination)**  
  OpenAI API runtime extraction with strict JSON Schema output mode and zero temperature ($T = 0.0$), eliminating false mismatches from synonymous carrier terminology (e.g., "Load Port" vs "Port of Loading").

- **Human-in-the-Loop Escalation**  
  Automatically flags unreadable scans, corrupt attachments, or discrepancies to an operator review queue with 1-click actions:  
  *Approve Discrepancy* • *Reject to Carrier* • *Request Clean Copy*

- **Audit-Ready Persistence**  
  Maintains secure attachment storage and relational verification audit logs backed by Supabase with Row-Level Security (RLS).

---

## 🛠️ Tech Stack

* **Frontend & Control Tower:** Next.js (App Router), React, Tailwind CSS
* **Backend & Verification API:** Python (FastAPI / Serverless handlers on Vercel)
* **Database & Persistence:** Supabase (PostgreSQL, Object Storage, Row-Level Security)
* **Extraction Engine:** OpenAI API (`gpt-4o` / `gpt-4o-mini` with structured JSON mode)
* **Document Parsing & OCR:** PyMuPDF (`fitz`), RapidOCR, `pypdf`, `python-docx`, `openpyxl`
* **Prompt Engineering:** Google Gemini
* **Cloud & Mailbox Ingestion:** Google Cloud Platform (Gmail API, OAuth 2.0), Vercel

---

## 📋 Prerequisites

Before getting started, make sure you have the following installed and configured:

* **Node.js:** Version 18.17.0 or higher ([Download Node.js](https://nodejs.org/en))
* **Python:** Version 3.10 or higher ([Download Python](https://www.python.org/downloads/))
* **Package Manager:** `npm` (bundled with Node), `pnpm`, or `yarn`
* **Supabase Account:** Free account at [supabase.com](https://supabase.com/)
* **OpenAI API Key:** Active key from [platform.openai.com](https://platform.openai.com/home)
* **Google Cloud Console Account:** Active account at [console.cloud.google.com](https://console.cloud.google.com/) with Gmail API enabled

---

## 🔐 Environment Variables

Create a `.env.local` file in the root directory of your project:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=[https://your-project-id.supabase.co](https://your-project-id.supabase.co)
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# OpenAI API Configuration
OPENAI_API_KEY=sk-your-openai-api-key

# Google Cloud / Gmail OAuth 2.0
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=[https://cargo-veritas.vercel.app/auth/gmail/callback](https://cargo-veritas.vercel.app/auth/gmail/callback)

# App Base URL
NEXT_PUBLIC_APP_URL=[https://cargo-veritas.vercel.app](https://cargo-veritas.vercel.app)
```

> [!WARNING]
> **Security Notice:** Never commit `.env.local` or any private API keys into your public repository. Ensure `.env.local` is listed in your `.gitignore` file.

---

## ⚠️ Google Cloud & Gmail Setup (Important for Evaluators)

### 📌 Sandbox Mode Notice
Because our Google OAuth App is currently in **Testing Mode** (unverified sandbox), Google’s security policies require that any Gmail account attempting to connect to the mailbox sync must be explicitly added as an Authorized Test User in Google Cloud Console.

* **Testing with Our Hosted App:**
  1. Visit [cargo-veritas.vercel.app](https://cargo-veritas.vercel.app) and sign up for an account.
  2. Reach out to Team AppleCat with your Gmail address. We will immediately add your account under **Google Cloud Console → OAuth consent screen → Test users**.
  3. Once added, you can sign in and link your operational Gmail mailbox without encountering `Error 403: access_denied`.
  *(Note: You can fully evaluate the platform without syncing live Gmail by using the pre-seeded simulation records in the dashboard).*

---

### 💻 If Setting Up Your Own Local Instance

1. In the [Google Cloud Console](https://console.cloud.google.com/), create a new project (e.g., `cargoveritas-dev`).
2. Go to **APIs & Services → Library**, search for **Gmail API**, and click **Enable**.
3. Go to **APIs & Services → OAuth consent screen**:
   - Select **External** and click **Create**.
   - Fill in the required app info (App name, User support email).
   - Under **Scopes**, add `https://www.googleapis.com/auth/gmail.readonly`.
   - Under **Test users**, click **+ Add Users** and enter your Gmail address.
4. Go to **APIs & Services → Credentials → Create Credentials → OAuth client ID**:
   - **Application type:** Web application
   - **Authorised JavaScript origins:**  
     `https://cargo-veritas.vercel.app` (or `http://localhost:3000` for local dev)
   - **Authorised redirect URIs:**  
     `https://cargo-veritas.vercel.app/auth/gmail/callback` (or `http://localhost:3000/auth/gmail/callback` for local dev)
5. Copy the generated Client ID and Client Secret into your `.env.local`.

---

## 🚀 Local Setup & Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/cargo-veritas.git](https://github.com/your-username/cargo-veritas.git)
cd cargo-veritas
```

### 2. Install Web Dependencies
```bash
npm install
# or: pnpm install / yarn install
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

---

## 🗄️ Supabase Database & Storage Setup

### 1. Database Schema
In your Supabase project dashboard, navigate to the **SQL Editor** and run the following script:

```sql
create table if not exists email_verifications (
  email_id text primary key,
  subject text,
  category text,
  status text,               -- 'OK', 'MISMATCH', 'NEEDS_REVIEW'
  review_reason text,        -- 'missing_attachment', 'unreadable', 'missing_value'
  defect_fields jsonb,       -- Array of mismatch field names
  si_data jsonb,             -- Extracted 7 SI fields
  bl_data jsonb,             -- Extracted 7 BL fields
  operator_action text,      -- 'APPROVED', 'REJECTED', 'PENDING'
  operator_notes text,
  created_at timestamp with time zone default timezone('utc'::text, now())
);

-- Enable Row Level Security (RLS)
alter table public.email_verifications enable row level security;

-- Policies: Allow authenticated users to view and update verifications
create policy "Allow authenticated read" on public.email_verifications
  for select using (auth.role() = 'authenticated');

create policy "Allow authenticated insert/update" on public.email_verifications
  for all using (auth.role() = 'authenticated');
```

### 2. Storage Buckets
1. In the **Supabase Dashboard**, navigate to **Storage → New Bucket**.
2. Name the bucket `shipping-documents`.
3. Toggle on **Public bucket** (or configure appropriate RLS policies for authenticated access) to enable retrieval of customer SI PDFs and carrier draft B/L attachments.

---

## 💻 Running the Application

### Start Development Server
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser to view the application.

### Production Build Test
To verify production readiness locally:
```bash
npm run build
npm start
```

---

## 📊 Benchmark Evaluation Pipeline (`submission.json`)

To run the automated verification pipeline across all benchmark test emails (`email_001` to `email_520`) and generate the hackathon autograder submission file:

```bash
python main.py
```

The script parses incoming emails, matches attachments, verifies all 7 fields, and writes the output directly to `submission.json` in the root directory.

---

## 🧪 Simulating Verification Scenarios

You can test the live comparison engine using the two baseline scenarios demonstrated during the hackathon:

### Scenario 1: Clean Pass (Auto-Cleared)
* **Input:** Shipping Instructions matching carrier Draft B/L across all 7 fields (Shipper, Consignee, Notify Party, Load Port, Discharge Port, Container Count, and Gross Weight).
* **Result:** System extracts all 7 fields in ~3 seconds, displays green checks across all fields, and commits the result directly to Supabase with status `OK`.

---

### Scenario 2: Gross Weight Discrepancy (Human Review)
* **Input:** Shipping Instructions stating 24,500 KG while Carrier Draft B/L reads 21,000 KG.
* **Result:** System matches companies and ports, highlights the Gross Weight mismatch in red, flags the discrepancy, and queues the record into the Human-in-the-Loop review queue for 1-click **Reject to Carrier** action.

---

## 🌐 Deployment (Vercel)

The easiest way to deploy this repository is using [Vercel](https://vercel.com):

1. Push your code to your GitHub repository.
2. In the Vercel dashboard, click **New Project** and import your `cargo-veritas` repository.
3. Configure your Environment Variables in Vercel:
   - `NEXT_PUBLIC_SUPABASE_URL`
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `OPENAI_API_KEY`
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `GOOGLE_REDIRECT_URI`
4. Click **Deploy**. Vercel will trigger automated CI/CD builds on every git push.

---

## 👥 Team & License

Built for the **Averis x Monash Hackathon 2026** by **Team AppleCat**.

* **Project:** CargoVeritas
* **Live Demo:** [cargo-veritas.vercel.app](https://cargo-veritas.vercel.app) (Click **Sign Up** to create an account and access the control tower).
* **Feedback & Questions:** Open an issue in this repository.
