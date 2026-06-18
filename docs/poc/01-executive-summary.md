# 1. Executive Summary

**Platform:** Atlas — Unified Knowledge Platform (UKP)
**Document type:** Proof of Concept — Technical & Architectural Proposal
**Status:** Draft for client review

---

## 1.1 The problem

Across the organization, knowledge is real but **fragmented**. The same answer a
person needs is often spread across a Confluence space, a SharePoint site, a
few PDFs on a shared drive, a closed Jira ticket, and a Slack thread — each
owned by a different team, each using different vocabulary, and each requiring
the right access.

The cost is not the storage of documents; it is the **human effort to find,
read, reconcile, and summarize them**. A single cross-team question — *"What is
our current data-retention policy for clinical trial documents, and which
projects already implement it?"* — can take an expert **hours** to answer, and
the answer is only as good as the documents that person happened to find.

Symptoms we hear repeatedly:

- "I know the answer exists somewhere — I just can't find it."
- "Every team documents the same thing differently."
- "By the time I've read everything, I'm not sure which version is current."
- "New joiners take months to learn where knowledge lives."

## 1.2 The proposed solution

**Atlas** is a scalable, extensible enterprise platform that **centralizes
knowledge across domains and projects** and lets people **ask a question once**
and receive a **single, clear, consolidated answer** — summarized from every
relevant page, with **inline citations** to the original sources.

Atlas does three things well:

1. **Unify** — Connectors continuously ingest content from many systems
   (wikis, document stores, ticketing, file shares, and more) into one
   normalized, searchable knowledge layer.
2. **Understand** — Content is parsed, chunked, embedded, and indexed for both
   semantic and keyword retrieval, enriched with metadata (domain, project,
   owner, freshness, access).
3. **Answer** — A retrieval-augmented generation (RAG) pipeline finds the most
   relevant passages across *all* sources and synthesizes a concise, grounded
   answer with citations — never a bare list of links.

Crucially, Atlas **respects existing permissions**: a user only ever sees
answers built from content they are already entitled to read.

## 1.3 What changes for the user

| Before | After (with Atlas) |
|--------|--------------------|
| Search returns 30 links; you open and read each. | You get one consolidated answer, with citations to expand. |
| You manually reconcile conflicting documents. | Atlas surfaces and flags conflicting/duplicate sources. |
| Knowledge lives in silos per team/tool. | One question spans every domain and project you can access. |
| Answers depend on who you ask. | Answers are consistent, grounded, and traceable. |

## 1.4 Why this is feasible now

- **RAG is mature enough for the enterprise**: grounding answers in retrieved
  source text makes them **auditable and citable**, which directly addresses
  trust and compliance concerns.
- **Pluggable, connector-first design**: new sources and domains are added as
  configuration + a small connector, not as a re-architecture.
- **Model-agnostic**: Atlas treats the LLM and the embedding model as swappable
  components, so we are never locked to a single vendor and can run in a
  private/VPC or on-prem deployment where required.

## 1.5 Value and outcomes

- **Time-to-answer** drops from hours of manual reading to seconds.
- **Consistency & trust**: every answer is grounded and cited, reducing
  reliance on tribal knowledge.
- **Faster onboarding** and reduced expert interrupt-load.
- **A reusable knowledge asset**: the same indexed layer powers search,
  Q&A, and future automation (e.g., agents, reports, compliance checks).

## 1.6 What the POC will demonstrate

A working end-to-end slice on **2–3 representative sources** and **1–2 priority
domains**, proving:

1. **Unified ingestion** of heterogeneous content.
2. **Cross-document consolidated answers** with inline citations.
3. **Permission-aware** retrieval (users only see what they may access).
4. **Measured quality** against a curated question set (relevance, groundedness,
   citation correctness, latency).
5. A clear path to **scale and extend** to all sources and domains.

See [`03-poc-plan.md`](./03-poc-plan.md) for scope, success criteria, and plan,
and [`02-architecture.md`](./02-architecture.md) for the full technical design.

## 1.7 The ask

Approval to run a **time-boxed POC** with access to representative source
systems and a small client-side working group (a product owner, a knowledge/SME
contact per domain, and an IT/security contact). Deliverables: a working demo,
a measured quality report, and a production reference architecture with a
phased rollout plan.
