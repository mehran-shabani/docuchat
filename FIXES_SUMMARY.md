# CI/CD Fixes Applied

## Issues Fixed

### 1. ✅ Ruff Formatting
- **Fixed:** `backend/app/api/routes/metrics.py`
- **Fixed:** `backend/app/services/tokens_meter.py`
- **Action:** Reformatted according to ruff standards

### 2. ✅ YAML Linting Issues
- **Fixed:** `infra/prometheus/alerts.yml`
  - Removed trailing spaces in HighErrorRate alert
  - Fixed HighCPUUsage formula (now properly calculates CPU percentage using quota/period)
- **Fixed:** `infra/prometheus/prometheus.yml`
  - Split long source_labels lines to be under 120 characters
- **Fixed:** `.github/workflows/ci.yml` and `.github/workflows/deploy.yml`
  - Removed all trailing spaces
  - Added proper shell quoting for variables
  - Updated action version for softprops/action-gh-release to v2

### 3. ✅ Markdown Linting Issues
- **Fixed:** `infra/README.md`
  - Added language specification to fenced code blocks (```text)
  - Wrapped bare URLs in angle brackets (<http://...>)
  - Added blank lines around lists

### 4. ✅ Security Issues
- **Fixed:** `scripts/test-devops.sh`
  - Replaced hardcoded Grafana credentials with environment variables
  - Removed unused TOTAL_CHECKS and PASSED_CHECKS variables

### 5. ✅ Grafana Dashboard Issues
- **Fixed:** `infra/grafana/dashboards/backend-overview.json`
  - Removed "dashboard" wrapper (Grafana provisioning expects raw dashboard model)
  - Improved histogram_quantile expressions with proper `sum by (le, ...)`
- **Fixed:** `infra/grafana/dashboards/token-usage.json`
  - Removed "dashboard" wrapper
  - Improved histogram_quantile expressions

## Testing Recommendations

After these fixes, the following CI checks should now pass:

1. ✅ Backend Lint & Test - ruff formatting should pass
2. ✅ Frontend Lint & Test - should continue passing
3. ✅ YAML Lint - all trailing spaces and line length issues resolved
4. ✅ Markdown Lint - fenced code blocks and URL issues fixed
5. ✅ Security scans - hardcoded credentials removed

## What Was Not Changed

- The core functionality remains intact
- All metric definitions unchanged
- Prometheus alert thresholds unchanged (only formula fixes)
- Dashboard panel configurations unchanged (only structure fixes)

## Next Steps

1. Commit these changes
2. Push to the PR branch
3. Wait for CI to run
4. All checks should now pass ✅
