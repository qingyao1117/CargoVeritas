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
To connect your personal or work Gmail address to the live deployment: Reach out to Team AppleCat with your Gmail address.We will immediately add your account under Google Cloud Console $\rightarrow$ OAuth consent screen $\rightarrow$ Test users.Once added, you can sign in and link your operational Gmail mailbox without encountering Google's Access Blocked: Authorization Error (Error 403: access_denied).

**If Setting Up Your Own Local Instance:**
1. Go to the Google Cloud Console.
2. Create a new project (e.g., cargoveritas-dev).
3. Navigate to APIs & Services $\rightarrow$ Library, search for Gmail API, and click Enable.
4. Navigate to APIs & Services $\rightarrow$ OAuth consent screen:
   Select External and click Create.
   Fill in the required app info (App name, User support email).
   Under Scopes, add the Gmail read/metadata scopes (e.g., https://www.googleapis.com/auth/gmail.readonly or https://www.googleapis.com/auth/gmail.modify).
   Under Test users, click + Add Users and enter your own Gmail account (and any evaluator emails).
5. Navigate to APIs & Services $\rightarrow$ Credentials:
   Click Create Credentials $\rightarrow$ OAuth client ID.
   Application type: Web application.
   Authorized redirect URIs:
      For local development: http://localhost:3000/api/auth/callback/google
      For production: https://your-domain.vercel.app/api/auth/callback/google
   Copy the generated Client ID and Client Secret into your .env.local.
