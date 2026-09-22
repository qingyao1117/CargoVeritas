**🚢 CargoVeritas — Automated Shipping Document Verification** <br />
**Averis x Monash Hackathon 2026** <br />
**Team: AppleCat** <br />
Live Prototype: https://cargo-veritas.vercel.app <br />

CargoVeritas is an automated SaaS Control Tower that connects directly to operational mailboxes, intelligently sorts incoming shipping communications, and automatically checks customer Shipping Instructions (SI) against ocean carrier draft Bills of Lading (B/L) across 7 mandatory logistics fields in seconds. Ambiguous or unreadable documents trigger a human-in-the-loop escalation rather than making blind guesses.

**📑 Table of Contents**
1. Key Features
2. Tech Stack
3. Prerequisites
4. Environment Variables
5. Google Cloud & Gmail Setup (Important for Evaluators)
6. Local Setup & Installation
7. Supabase Database & Storage Setup
8. Running the Application
9. Simulating Verification Scenarios
10. Deployment (Vercel)
11. Team & License

**✨ Key Features** <br />
**1. Inbox Intelligence Engine:** Synchronizes operational inboxes and categorizes incoming messages into 5 clear buckets (Bill of Lading Comparison, Shipping Instruction Request, Invoice Query, General Update, Spam). <br />
**2. Automated 7-Field Cross-Alignment:** Compares Shipper, Consignee, Notify Party, Port of Loading, Port of Discharge, Container Count, and Gross Weight (kg) side-by-side in ~3 seconds. <br />
**3. Deterministic Zero-Hallucination Extraction:** OpenAI API runtime extraction with strict JSON Schema output mode and zero temperature ($T = 0.0$), eliminating false mismatches from synonymous carrier terminology (e.g., "Load Port" vs "Port of Loading").<br />
**4. Human-in-the-Loop Escalation:** Automatically flags unreadable scans, corrupt attachments, or discrepancies to an operator review queue with 1-click actions (Approve Discrepancy, Reject to Carrier, or Request Amended Docs). <br />
**5. Enterprise Persistence & Auditability:** Secure document storage and tamper-evident relational logs powered by Supabase with Row-Level Security (RLS). <br />

**🛠 Tech Stack** <br />
**1. Frontend & Web Framework:** Next.js (App Router) / React, Tailwind CSS <br />
**2. Authentication & Backend:** Supabase (PostgreSQL, Object Storage, Row-Level Security) <br />
**3. AI & Prompting Engine:** OpenAI API (gpt-4o / gpt-4o-mini with structured JSON mode), Google Gemini (Prompt Engineering) <br />
**4. Mailbox & Cloud Infrastructure:** Google Cloud Platform (Gmail API, OAuth 2.0), Vercel <br />

**📋 Prerequisites** <br />
Before getting started, make sure you have the following installed and configured: <br />
**1. Node.js:** Version 18.17.0 or higher [Download Node.js](https://nodejs.org/en) <br />
**2. Package Manager:** npm (bundled with Node), pnpm, or yarn <br />
**3. Supabase Account:** A free account at [supabase.com] (https://supabase.com/) <br />
**4. OpenAI API Key:** An active key from [platform.openai.com] (https://platform.openai.com/home) <br />
**5. Google Cloud Console Account:** An active account at [console.cloud.google.com] (https://console.cloud.google.com/) to authorize Gmail API access. <br />

**🔐 Environment Variables**
Create a .env.local file in the root directory of your project:
```
**Supabase Configuration (Settings > API in your Supabase dashboard)**
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

**OpenAI API Configuration**
OPENAI_API_KEY=sk-your-openai-api-key

**Google Cloud / Gmail OAuth 2.0**
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:3000/api/auth/callback/google

**Optional / App Base URL**
NEXT_PUBLIC_APP_URL=http://localhost:3000
```
**⚠️ Security Notice:** Never commit .env.local or any private API keys into your public repository. Ensure .env.local is listed in your .gitignore file.

**⚠️ Google Cloud & Gmail Setup** (Important for Evaluators) <br />
**Notice for Hackathon Judges & Testers:** <br />
Because our Google OAuth App is currently in Testing Mode (unverified sandbox), Google’s security policies require that any Gmail account attempting to connect to the mailbox sync must be explicitly added as an Authorized Test User in Google Cloud Console.

**If Testing with Our Hosted App:** <br />
To connect your personal or work Gmail address to the live deployment: Reach out to Team AppleCat with your Gmail address.We will immediately add your account under Google Cloud Console $\rightarrow$ OAuth consent screen $\rightarrow$ Test users. Once added, you can sign in and link your operational Gmail mailbox without encountering Google's Access Blocked: Authorization Error (Error 403: access_denied).

**If Setting Up Your Own Local Instance:**
1. Go to the Google Cloud Console.
2. Create a new project (e.g., cargoveritas-dev).
3. Navigate to APIs & Services $\rightarrow$ Library, search for Gmail API, and click Enable.
4. Navigate to APIs & Services $\rightarrow$ OAuth consent screen:
   Select External and click Create. <br />
   Fill in the required app info (App name, User support email). <br />
   Under Scopes, add the Gmail read/metadata scopes (e.g., https://www.googleapis.com/auth/gmail.readonly or https://www.googleapis.com/auth/gmail.modify). <br />
   Under Test users, click + Add Users and enter your own Gmail account (and any evaluator emails). <br />
5. Navigate to APIs & Services $\rightarrow$ Credentials:
   Click Create Credentials $\rightarrow$ OAuth client ID. <br />
   Application type: Web application. <br />
   Authorized redirect URIs: <br />
      For local development: http://localhost:3000/api/auth/callback/google <br />
      For production: https://your-domain.vercel.app/api/auth/callback/google <br />
   Copy the generated Client ID and Client Secret into your .env.local. <br />

**🚀 Local Setup & Installation**
1. Clone the Repository
```
git clone https://github.com/your-username/cargo-veritas.git
cd cargo-veritas
```

2. Install Dependencies
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
