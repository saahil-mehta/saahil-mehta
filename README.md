<a href="https://saahil.co.uk">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
    <img alt="I lead data and AI at South Pole, and I still ship the systems myself. Associate Director, Data &amp; Insights · South Pole · London" src="assets/banner-light.svg" width="100%">
  </picture>
</a>

## Now

I lead a team of six and own the data platform, the marts and the reporting stack for the whole company.

Most of my time goes into Orca, the enterprise AI assistant I built for the business, and the governed platform underneath it: a semantic layer that tells Orca what our data means, self-hosted orchestration, access governance that runs itself, and cost monitoring across every project we have.

I wrote the data strategy the executive committee adopted, and I commit code most days.


## Work

The systems in production at South Pole, designed and built by me with the team.

- **Orca** · AI assistant, in production since Jun 2026. South Pole's enterprise AI assistant, open to the whole company. Deep research over the web and company data, South Pole-format documents, decks and sales proposals, scheduled runs, memory, and sharing with version history.
- **Orca Semantics** · Semantic layer, in build since Jul 2026. A governed semantic layer on self-hosted OpenMetadata: plain-English definitions, certified metric SQL, a glossary and named owners per domain, all version controlled.
- **Orca Visuals** · Visualisation, in build since Aug 2026. The visualisation layer on top of Orca Semantics: dashboards and metrics defined as code against the certified definitions, so a chart and Orca's answer agree.
- **Data Marts Core** · Orchestration, in production since Sep 2026. Orchestration for 1,800+ dbt models, migrated from dbt Cloud to self-hosted Dagster on GKE in three weeks.
- **Data Foundation Plan** · Strategy, in production since Aug 2026. The company data strategy, written, costed and taken to ExCo: seven workstreams to 2028 covering the semantic layer, orchestration, visualisation, the AI platform, data quality at scale, access governance and SLAs.
- **Data Access Governance** · Governance, in production since Oct 2026. Self-service data access. A request names the access group and the reason, mails the data owner, and opens a Terraform pull request that grants the group read access, through an org-owned GitHub App.
- **Cost Deep Dive** · FinOps, in production since Jan 2025. FinOps across 195 GCP projects and 60 services: spend by app, by service, by day, with P99 anomaly detection that emails me when an app breaks its own baseline.
- **Enterprise Data Platform Migration** · Platform, in production since Mar 2024. Migrated 18,000+ cloud resources from Pulumi to modular Terraform. Standardised IAM, networking, and policy-as-code so five business units now share one platform without stepping on each other.

All systems, with how each is built: [saahil.co.uk/projects](https://saahil.co.uk/projects).

## Still shipping

Commits over the last twelve months, drawn by GitHub beneath this page.

## How it fits together

The systems in production, what each one does and what flows between them.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/platform-dark.svg">
  <img alt="How it fits together. The systems in production, what each one does and what flows between them." src="assets/platform-light.svg" width="100%">
</picture>

Owners are named once, in the semantic layer, and access approvals, quality routing and Orca's context all reuse them.

## Experience

Seven years across South Pole, Publicis Groupe and WPP.

- **Associate Director, Data & Insights**, South Pole, Jul 2026 to present. Lead a team of six and own the data platform, marts and reporting stack for the whole company. Set the data strategy the executive committee adopted, and build the systems above with the team.
- **Lead Specialist, Data Engineering**, South Pole, Mar 2024 to Jul 2026. Own the climate-finance data estate: the move to Terraform, governed services that let AI workloads reach sensitive carbon-credit data without breaking access controls, and the first company-wide release of the AI assistant.
- **Senior Data Engineer II**, Publicis Groupe, Digitas UK, Jul 2023 to Mar 2024. Cut flagship GCP + Airflow workloads from four hours to two. Built GitHub Actions CI/CD that replaced manual deployments.

Full history: [saahil.co.uk/experience](https://saahil.co.uk/experience).

## Beyond work

Mentoring, a museum archive, and where I studied.

- **MERL Visitor Insight Engine**, Museum of English Rural Life · Volunteer, 2025 - Present.
- **[Data Science Festival Mentorship](https://datasciencefestival.com)**, Data Science Festival · Mentor, 2026 - Present.
- **Google Developer Specialist**, Google · Invite-only Programme, 2026.
- **Master of Science in Data Analytics**, University of Strathclyde (Business School), 2022 - 2023. First-Class Honours / Distinction.

## Let's talk.

About building AI systems people actually use, leading data teams, or your data and cloud estate.

[self@saahil.co.uk](mailto:self@saahil.co.uk) · [LinkedIn](https://www.linkedin.com/in/saahil-mehta) · [Book a call](https://calendly.com/saahil_mehta/30min)

<sub>Also available as [resume.pdf](https://saahil.co.uk/Saahil-Mehta-Resume.pdf) · [resume.json](https://saahil.co.uk/resume.json) · [cv.md](https://saahil.co.uk/cv.md) · [llms.txt](https://saahil.co.uk/llms.txt) · [status.json](https://saahil.co.uk/status.json). This page re-renders every morning from status.json, the same source the site builds from.</sub>
