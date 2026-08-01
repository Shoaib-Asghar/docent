---
sidebar_position: 4
---

# Deployment & DevOps

## What we set up

- **Containerization** — Docker, so an application runs identically in development, staging, and production
- **CI/CD pipelines** — GitHub Actions, running tests automatically on every change and deploying only what passes
- **Hosting** — a cost-appropriate VPS (DigitalOcean, Hetzner) for smaller projects, migrating to AWS/GCP when a client needs scale, compliance, or specific infrastructure
- **Monitoring** — uptime checks and structured logging, so issues are caught before a client notices them

## Why this matters

A working app that nobody can safely update or deploy isn't actually finished — it's a liability the client inherits. We set up the pipeline once, correctly, so future changes ship without the fear of breaking production.

## Typical pricing

CI/CD pipeline setup: **$400–$800** depending on the target infrastructure and existing codebase complexity.
