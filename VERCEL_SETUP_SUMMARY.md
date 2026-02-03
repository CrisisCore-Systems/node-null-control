# Vercel Auto-Deploy Setup - Summary

## ✅ What Has Been Configured

This pull request sets up **automatic Vercel deployment on every push** to the repository. Here's what has been added:

### 1. GitHub Actions Workflow (`.github/workflows/vercel-deploy.yml`)
- Triggers on push to `main` and `develop` branches
- Also triggers on pull requests to these branches
- Automatically deploys to Vercel:
  - **Production** deployment for `main` branch
  - **Preview** deployments for other branches and PRs

### 2. Documentation
- **`docs/VERCEL_DEPLOYMENT.md`**: Complete setup guide with step-by-step instructions
- **`README.md`**: Added reference to deployment documentation
- **`docs/OPERATIONS.md`**: Updated with automatic deployment information
- **`docs/QUICKSTART.md`**: Added deployment section

### 3. Deployment Optimization
- **`.vercelignore`**: Excludes unnecessary files from deployment (tests, build artifacts, internal docs)
  - Only deploys what's needed: `forge/`, `api/`, `monetization/assets/`, and `vercel.json`

## 🔧 What You Need to Do

The workflow is ready but requires **one-time setup** of GitHub Secrets:

### Step 1: Create/Link Vercel Project
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New" → "Project"
3. Import the `CrisisCore-Systems/node-null-control` repository
4. Configure:
   - Framework: Other
   - Root Directory: `.` (repository root)
   - Leave Build/Output/Install commands empty

### Step 2: Get Vercel Credentials
You need three pieces of information:

#### A. Vercel Token
1. Go to [Vercel Account Settings → Tokens](https://vercel.com/account/tokens)
2. Click "Create Token"
3. Name it (e.g., "GitHub Actions")
4. Copy the token

#### B. Project ID and Org ID
Run these commands locally:
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Link to your project (in repo root)
cd /path/to/node-null-control
vercel link
```

This creates `.vercel/project.json` with your IDs:
```json
{
  "projectId": "prj_xxxxxxxxxxxxxxxxxxxx",
  "orgId": "team_xxxxxxxxxxxxxxxxxxxx"
}
```

### Step 3: Add GitHub Secrets
1. Go to https://github.com/CrisisCore-Systems/node-null-control/settings/secrets/actions
2. Click "New repository secret" and add:

   - **Name**: `VERCEL_TOKEN`
     - **Value**: Your token from Step 2A

   - **Name**: `VERCEL_ORG_ID`
     - **Value**: The `orgId` from `.vercel/project.json`

   - **Name**: `VERCEL_PROJECT_ID`
     - **Value**: The `projectId` from `.vercel/project.json`

### Step 4: Test It!
Once secrets are added:
1. Merge this PR to `main`
2. Watch the deployment in:
   - [GitHub Actions tab](https://github.com/CrisisCore-Systems/node-null-control/actions)
   - [Vercel Dashboard](https://vercel.com/dashboard)
3. Your site will be live at your Vercel project URL

## 🎯 How It Works

After setup:
- **Push to `main`** → Automatic production deployment
- **Push to other branches** → Automatic preview deployment
- **Open PR** → Automatic preview deployment (Vercel bot comments with URL)
- **No manual work needed** → Everything is automatic!

## 📁 What Gets Deployed

The deployment includes:
- **`/forge/`** - The conversion interface (routed to `/` via `vercel.json`)
- **`/api/`** - Serverless functions (like `/api/identity.js`)
- **`/monetization/assets/`** - Asset registry (if needed)

Everything else (docs, scripts, tests, etc.) is excluded via `.vercelignore`.

## 🔒 Environment Variables (Optional)

If you want to enable the identity capture API:
1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add `IDENTITY_WEBHOOK_URL` with your webhook endpoint
3. This enables the `/api/identity` endpoint for form submissions

## 📚 Full Documentation

For detailed information, see:
- **Complete setup guide**: `docs/VERCEL_DEPLOYMENT.md`
- **Quick start**: `docs/QUICKSTART.md`
- **Operations**: `docs/OPERATIONS.md`

## ❓ Troubleshooting

If the workflow fails after merging:
1. Verify all three secrets are set correctly
2. Check the Actions tab for error messages
3. Common issues:
   - Token expired → Create new token
   - Wrong project ID → Re-run `vercel link`
   - Missing secrets → Double-check all three are added

## 🎉 That's It!

Once you add the three secrets, your Vercel deployments will be fully automated. Every push will trigger a deployment, and you'll never need to manually deploy again!
