# Vercel Deployment Setup

This repository is configured for automatic deployment to Vercel on every push.

## Automatic Deployment Workflow

The `.github/workflows/vercel-deploy.yml` workflow handles automatic deployments:
- **Production deployments**: Triggered on push to `main` branch
- **Preview deployments**: Triggered on push to other branches and pull requests

## Prerequisites

Before the automatic deployments can work, you need to configure GitHub Secrets:

### 1. Create a Vercel Project

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New" → "Project"
3. Import this GitHub repository
4. Configure project settings:
   - **Framework Preset**: Other
   - **Root Directory**: `.` (repository root)
   - **Build Command**: Leave empty (Vercel will use `vercel.json`)
   - **Output Directory**: Leave empty
   - **Install Command**: Leave empty or `npm install` if needed

### 2. Get Your Vercel Token

1. Go to [Vercel Account Settings → Tokens](https://vercel.com/account/tokens)
2. Click "Create Token"
3. Give it a name (e.g., "GitHub Actions")
4. Set expiration as needed
5. Copy the token (you won't be able to see it again)

### 3. Get Your Vercel Project Details

You can find these in your Vercel project settings or by running:

```bash
# Install Vercel CLI locally
npm install -g vercel

# Login to Vercel
vercel login

# Link to your project (run in the repository root)
vercel link

# This creates a .vercel/project.json file with your project details
```

The `.vercel/project.json` will contain:
```json
{
  "projectId": "prj_xxxxxxxxxxxxxxxxxxxx",
  "orgId": "team_xxxxxxxxxxxxxxxxxxxx"
}
```

### 4. Add GitHub Secrets

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret" and add the following:

   - **Name**: `VERCEL_TOKEN`
     - **Value**: Your Vercel token from step 2

   - **Name**: `VERCEL_ORG_ID`
     - **Value**: The `orgId` from `.vercel/project.json`

   - **Name**: `VERCEL_PROJECT_ID`
     - **Value**: The `projectId` from `.vercel/project.json`

### 5. Optional: Environment Variables

If your project needs environment variables (like `IDENTITY_WEBHOOK_URL` for the identity API):

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add your environment variables:
   - `IDENTITY_WEBHOOK_URL`: Your webhook endpoint URL
   - Set the environment: Production, Preview, or Development

## How It Works

1. When you push to any branch, GitHub Actions triggers the workflow
2. The workflow:
   - Checks out your code
   - Installs Vercel CLI
   - Pulls Vercel environment configuration
   - Builds the project using Vercel's build system
   - Deploys to Vercel (production for `main`, preview for others)
3. You'll see the deployment status in:
   - GitHub Actions tab
   - Vercel Dashboard
   - Pull request comments (Vercel bot will comment with preview URL)

## Manual Deployment (Optional)

You can still deploy manually if needed:

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

## Project Structure

The `vercel.json` configuration:
- Routes root (`/`) to `/forge/` (the conversion interface)
- Configures security headers for `/forge/` and `/api/` routes
- Enables serverless functions in the `/api/` directory

## Disabling Auto-Deploy

If you want to disable automatic deployments:

1. **Option A**: Delete or rename `.github/workflows/vercel-deploy.yml`
2. **Option B**: Disable the workflow in GitHub Actions settings
3. **Option C**: Remove the GitHub Secrets (workflow will fail without them)

## Troubleshooting

### Workflow fails with "401 Unauthorized"
- Check that `VERCEL_TOKEN` is valid and not expired
- Create a new token and update the secret

### Workflow fails with "Project not found"
- Verify `VERCEL_PROJECT_ID` matches your Vercel project
- Verify `VERCEL_ORG_ID` matches your Vercel account/team

### Deployment succeeds but site doesn't work
- Check Vercel deployment logs in the Vercel Dashboard
- Verify environment variables are set correctly
- Check that `vercel.json` configuration is correct

### Want to deploy only on specific branches
Edit `.github/workflows/vercel-deploy.yml` and modify the `branches` list:
```yaml
on:
  push:
    branches:
      - main  # Only deploy main branch
```

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel CLI Documentation](https://vercel.com/docs/cli)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
