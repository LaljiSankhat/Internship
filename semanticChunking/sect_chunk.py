
kb_text = """Project Knowledge Base
1. Project Overview
Project Name: Project Ether Objective: Deploy the new recommendation engine to the production cluster. Primary Focus: Upgrading the "Suggested for You" section to meet strict latency and performance requirements using a collaborative filtering model.

2. Goals & Success Criteria
Latency Target: 200 milliseconds for the "Suggested for You" section.
Current Status: Staging environment is currently meeting this target at ~185ms.
Model Performance: Precision is currently at 87.5% (post-quantization), which is within the acceptable range.
Compliance: GDPR compliance for new regions (specifically regarding data scrubbing).
3. Scope (In-Scope / Out-of-Scope)
In-Scope:

Development and refinement of the collaborative filtering model.
Implementation of vector similarity search using Milvus.
Model quantization to optimize latency.
Kubernetes infrastructure setup for model serving.
API documentation for the front-end team.
Data privacy auditing and script updates for new regions.
Implementation of a fallback strategy to the legacy heuristic system.
Out-of-Scope:

N/A
4. Architecture / Technical Design
Vector Database: Milvus has been officially adopted to handle high-dimensional embeddings, replacing the previous setup.
Model Serving: Kubernetes sidecars are used for serving the model.
Data Processing: Spark jobs are utilized for the training pipeline.
Testing Data: Synthetic data is currently used for testing.
Fallback Mechanism: System will revert to the old heuristic-based recommendation system if Milvus latency crosses a defined threshold.
5. Features & Requirements
Recommendation Engine: Collaborative filtering model.
Infrastructure:
Spark job optimization has been partially addressed via feature pruning and parallelization (training time reduced to ~4 hours).
Documentation: Swagger documentation required for front-end integration (Draft complete, authentication section requires clarification).
6. Decisions Log
2026-02-XX: Adopt Milvus for Vector Search
Decision: Officially adopt Milvus as the vector database solution.
Rationale: It handles high-dimensional embeddings better than the current setup.
Impacted Components: Vector similarity search, "Suggested for You" architecture.
2026-02-XX: Fallback Strategy Defined
Decision: Implement a partial rollback to the old heuristic-based recommendation system if Milvus latency crosses a defined threshold.
Rationale: Ensures system stability and availability during peak traffic or Milvus instability without requiring a full deployment rollback.
Impacted Components: API Gateway, Recommendation Logic.
2026-02-XX: GPU Budget Approval (Staging)
Decision: Budget approved for additional GPU instances in the staging environment.
Constraint: Production scaling will require a separate sign-off.
7. Timeline & Milestones
February 15, 2026: Deadline for model quantization completion.
February 18, 2026: Deadline for Swagger API documentation completion.
February 20, 2026: Deadline for Kubernetes (K8s) infrastructure setup.
Upcoming: Go/No-Go decision for production deployment targeted for next week.
8. Action Items & Ownership
Owner	Task	Deadline	Status
Marcus (ML Engineer)	Complete model quantization to assist with latency targets.	February 15, 2026	Completed
Lyla (DevOps)	Set up Kubernetes sidecars for model serving.	February 20, 2026	Completed
Lyla (DevOps)	Document fallback thresholds and rollback steps for the heuristic strategy.	TBD	Planned
David	Finalize Swagger documentation (specifically the authentication section).	February 18, 2026	In Progress
Lyla (DevOps)	Optimize Spark jobs (pending feature set requirements from Marcus).	TBD	In Progress
Sarah (Project Lead)	Verify budget availability for extra GPU instances in staging.	TBD	Completed
Sarah (Project Lead)	Address minor updates to data scrubbing script for GDPR compliance.	TBD	Planned
Sarah (Project Lead)	Secure sign-off for production GPU scaling.	TBD	Planned
9. Risks, Blockers & Dependencies
Training Pipeline Latency: Training time has improved from six hours to four hours via feature pruning and parallelization.
Data Privacy & Compliance:
Current data scrubbing script requires minor updates to be fully GDPR compliant for the new region.
Status: Legal feedback received; fixes are defined and considered manageable.
Data Drift: Synthetic testing data may not reflect edge cases in the European market.
Risk: If real data differs significantly, model performance (currently 87.5%) could decrease.
Infrastructure Resilience: Fallback strategy defined (heuristic model), mitigating previous risk regarding Milvus cluster failure.
Documentation: Swagger documentation is incomplete pending clarification on the authentication section.
10. Open Questions & Pending Clarifications
Production Scaling: When will the sign-off for production GPU scaling occur? (Staging is approved).
Authentication Specs: What are the specific requirements for the authentication section in the Swagger documentation?

"""


import re

def split_by_sections(text):
    # Matches numbered headers like "1. Title", "10. Title"
    pattern = r"(?:^|\n)(\d+\.\s+[^\n]+)"
    parts = re.split(pattern, text)

    sections = []
    current_title = None
    current_body = []

    for part in parts:
        part = part.strip()
        if re.match(r"\d+\.\s+", part):
            if current_title:
                sections.append({
                    "title": current_title,
                    "content": "\n".join(current_body).strip()
                })
            current_title = part
            current_body = []
        else:
            current_body.append(part)

    if current_title:
        sections.append({
            "title": current_title,
            "content": "\n".join(current_body).strip()
        })

    return sections



from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import SentenceTransformerEmbeddings


embeddings = SentenceTransformerEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

chunker = SemanticChunker(
    embeddings=embeddings,
    breakpoint_threshold_type="percentile"
)

sections = split_by_sections(kb_text)
for section in sections:
    print(section["title"])
    print(section["content"])
    print("-"*100)

final_chunks = []

for section in sections:
    section_chunks = chunker.split_text(section["content"])

    for i, chunk in enumerate(section_chunks):
        final_chunks.append({
            "section": section["title"],
            "chunk_index": i,
            "text": chunk
        })

print("hell")
print("Final Chunks type: ",type(final_chunks))
for chunk in final_chunks:
    print("Section: ",chunk["section"])
    print("Chunk Index: ",chunk["chunk_index"])
    print("Text: ",chunk["text"])
    print("-"*100)