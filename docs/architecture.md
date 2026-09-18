# Architecture decisions

## Why a workflow instead of an agent

Invoice reconciliation has known stages and objective checks. A fixed workflow makes failures observable and keeps the model away from the final financial decision. Gemini performs schema-guided perception; deterministic code owns item matching, decimal arithmetic, discrepancies, and review history.

## Trust boundaries

- Uploaded files are untrusted. Their printed instructions are explicitly treated as content.
- The API key stays in the backend environment and is never returned to the browser.
- Model output is parsed through Pydantic before reconciliation.
- High-value fields and rows require locally resolved source evidence. Missing support creates a review flag.
- SQLite preserves job status, results, errors, provider usage, and reviewer changes across restarts.
- The configured development spend guard checks accumulated estimated Gemini cost before starting new inference.

## Failure behavior

Provider errors, invalid structured output, document limits, and parser errors move the job to `failed` with a visible message. There is no silent fallback to sample data. A worker restart does not corrupt completed results; queued/processing job recovery is the next production extension.

## Matching policy

Rows match by case-insensitive SKU when available. Otherwise, normalized description similarity must be at least `0.55`; close competing candidates create an ambiguous-match review item. Money uses `Decimal` rounded to cents. Currency mismatches stop meaningful price comparison and remain critical findings.
