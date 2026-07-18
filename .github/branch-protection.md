# Branch Protection Setup

GitHub branch protection rules cannot be set via files — they must be configured in **Settings → Branches**.

Apply these settings to the `main` branch:

## Required settings for `main`

1. Go to: `Settings` → `Branches` → `Add branch ruleset` (or `Add rule`)
2. Branch name pattern: `main`
3. Enable:
   - ✅ **Require a pull request before merging**
     - Require approvals: `1`
     - Dismiss stale pull request approvals when new commits are pushed: ✅
   - ✅ **Require status checks to pass before merging**
     - Add these required checks:
       - `Validate Manifest Schema`
       - `Download & Verify SHA-256`
       - `ClamAV Malware Scan`
       - `VirusTotal Scan`
       - `Update PR Status`
     - ✅ Require branches to be up to date before merging
   - ✅ **Require conversation resolution before merging**
   - ✅ **Do not allow bypassing the above settings**
   - ✅ **Restrict who can push to matching branches** (add yourself/team)

## For the API (if you want to automate it via gh CLI)

```bash
gh api repos/kyrosystems/makulinux-packages/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["Validate Manifest Schema","Download & Verify SHA-256","ClamAV Malware Scan","VirusTotal Scan","Update PR Status"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  --field restrictions=null
```

## Required secrets

Go to `Settings` → `Secrets and variables` → `Actions`:

| Secret name | Where to get it |
|-------------|-----------------|
| `VIRUSTOTAL_API_KEY` | https://www.virustotal.com/gui/join-us (free tier = 500 req/day) |
