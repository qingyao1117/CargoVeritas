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

**✨ Key Features**
**📥 Inbox Intelligence Engine:** Synchronizes operational inboxes and categorizes incoming messages into 5 clear buckets (Bill of Lading Comparison, Shipping Instruction Request, Invoice Query, General Update, Spam).
**🔍 Automated 7-Field Cross-Alignment:** Compares Shipper, Consignee, Notify Party, Port of Loading, Port of Discharge, Container Count, and Gross Weight (kg) side-by-side in ~3 seconds.
**🎯 Deterministic Zero-Hallucination Extraction:** OpenAI API runtime extraction with strict JSON Schema output mode and zero temperature ($T = 0.0$), eliminating false mismatches from synonymous carrier terminology (e.g., "Load Port" vs "Port of Loading").
**🙋 Human-in-the-Loop Escalation:** Automatically flags unreadable scans, corrupt attachments, or discrepancies to an operator review queue with 1-click actions (Approve Discrepancy, Reject to Carrier, or Request Amended Docs).
**🔒 Enterprise Persistence & Auditability:** Secure document storage and tamper-evident relational logs powered by Supabase with Row-Level Security (RLS).

**🛠 Tech Stack**
**Frontend & Web Framework:** Next.js (App Router) / React, Tailwind CSS
**Authentication & Backend:** Supabase (PostgreSQL, Object Storage, Row-Level Security)
**AI & Prompting Engine:** OpenAI API (gpt-4o / gpt-4o-mini with structured JSON mode), Google Gemini (Prompt Engineering)
**Mailbox & Cloud Infrastructure:** Google Cloud Platform (Gmail API, OAuth 2.0), Vercel

**📋 Prerequisites**
Before getting started, make sure you have the following installed and configured:
**Node.js:** Version 18.17.0 or higher [Download Node.js](https://nodejs.org/en)
**Package Manager:** npm (bundled with Node), pnpm, or yarn
**Supabase Account:** A free account at [supabase.com] (https://supabase.com/)
**OpenAI API Key:** An active key from [platform.openai.com] (https://platform.openai.com/home)
**Google Cloud Console Account:** An active account at [console.cloud.google.com] (https://console.cloud.google.com/) to authorize Gmail API access.

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
