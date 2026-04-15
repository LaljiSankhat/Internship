import nltk
nltk.download('punkt')

kb_text = """# Project Knowledge Base

## 1. Project Overview
**Project Name:** Project Ether Production Rollout
**Current Status:** **GO for Production Deployment** (Authorized as of final review)
**Description:** Project Ether involves the rollout of a quantized machine learning model into a production environment. The system utilizes a Kubernetes-based infrastructure with a Milvus vector database backend and includes automated fallback mechanisms to ensure service continuity.

## 2. Goals & Success Criteria
*   **Performance:** Maintain high precision (target: ~87.5%) and acceptable inference latency under load.
*   **Reliability:** Ensure infrastructure stability and successful failover mechanisms.
*   **Compliance:** Achieve full GDPR compliance for the new European region.
*   **Safety:** Ensure rollback capabilities are available and rehearsed.

## 3. Scope (In-Scope / Out-of-Scope)
**In-Scope:**
*   Deployment of the quantized model to production.
*   Kubernetes sidecar deployment.
*   Milvus cluster setup and stress testing.
*   GDPR data scrubbing implementation.
*   Documentation of API and authentication for frontend integration.

**Out-of-Scope:**
*   Future scaling beyond initial production capacity (requires separate financial sign-off).

## 4. Architecture / Technical Design
*   **Model:** Quantized model (currently stable in staging).
*   **Infrastructure:** Kubernetes environment utilizing sidecars.
*   **Database:** Milvus cluster (configured for high availability and failover).
*   **Fallback Strategy:**
    *   **Trigger:** Automatic routing triggered if Milvus latency exceeds defined thresholds or error rates spike.
    *   **Mechanism:** Traffic routes to a heuristic-based recommendation system upon trigger.
*   **API Documentation:** Swagger documentation is finalized, specifically regarding the authentication section.

## 5. Features & Requirements
*   **Inference Latency:** ~180-190ms under simulated peak load.
*   **Precision:** Steady at 87.5%.
*   **Data Handling:** Includes data scrubbing scripts to satisfy GDPR requirements.
*   **Monitoring:** Drift detection metrics and alerts have been implemented to monitor for data drift post-launch.

## 6. Decisions Log
*   **2023-XX-XX: Production Deployment Authorization**
    *   **Decision:** Project is officially "GO" for production deployment.
    *   **Rationale:** Successful confirmation of readiness across model performance (stable latency/precision), infrastructure (Kubernetes/Milvus stability), compliance (GDPR approval), and documentation.
    *   **Scope:** Full production rollout as scheduled.
*   **2023-XX-XX: Fallback Mechanism Implementation**
    *   **Decision:** Adopted automatic traffic routing to heuristic system upon Milvus failure/threshold breach.
    *   **Rationale:** To ensure availability and graceful degradation during database stress.
*   **2023-XX-XX: Budget & Scaling**
    *   **Decision:** Finance approved current production deployment.
    *   **Constraint:** Scaling beyond initial capacity requires a new sign-off.

## 7. Timeline & Milestones
*   **Completed:**
    *   Stabilization of quantized model in staging.
    *   Infrastructure stress and failover testing (Milvus/Kubernetes).
    *   GDPR legal review and validation.
    *   Final "Go/No-Go" Review.
*   **Current Phase:** Production Deployment (In Progress/Initiated).

## 8. Action Items & Ownership
*   **Post-Launch Monitoring:**
    *   **Owner:** Engineering/Data Team
    *   **Task:** Monitor data drift metrics and alerts closely post-launch.
    *   **Status:** Planned (Post-Deployment).
*   **Deployment Execution:**
    *   **Owner:** Engineering Team
    *   **Task:** Proceed with production rollout as scheduled.
    *   **Status:** Active.

## 9. Risks, Blockers & Dependencies
*   **Risk:** Data Drift
    *   **Mitigation:** Drift detection metrics and alerts are in place; team is prepared to react quickly to abnormal behavior.
*   **Risk:** Infrastructure Latency/Failure
    *   **Mitigation:** Rehearsed rollback procedures (partial and full) and automated fallback to heuristic systems are active.

## 10. Open Questions & Pending Clarifications
*   *None identified.* All critical compliance, technical, and budgetary items were resolved during the final review.

## 11. Glossary
*   **Quantized Model:** A compressed version of the machine learning model optimized for inference latency and resource efficiency.
*   **Milvus:** Open-source vector database used for the production backend.
*   **Heuristic-based recommendation system:** The fallback system used if the primary ML model or database fails performance thresholds.
*   **GDPR:** General Data Protection Regulation (compliance required for the new region)."""


from semantic_chunker.core import SemanticChunker
from nltk.tokenize import sent_tokenize



import re

def split_by_sections(text: str):
    """
    Splits a markdown document into numbered sections like:
    ## 1. Project Overview
    ## 10. Open Questions & Pending Clarifications
    """

    # Match markdown headers with numbered sections
    header_pattern = re.compile(
        r"^##\s+(\d+\.\s+.+)$",
        re.MULTILINE
    )

    matches = list(header_pattern.finditer(text))

    sections = []

    for i, match in enumerate(matches):
        title = match.group(1).strip()

        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        content = text[start:end].strip()

        sections.append({
            "title": title,
            "content": content
        })

    return sections






def test_semantic_chunker(text):
    sections = split_by_sections(text)

    for section in sections:
        # Sentence tokenization
        sentences = sent_tokenize(section["content"])

        # Convert into required chunk format
        chunks = [{"text": sentence} for sentence in sentences]

        chunker = SemanticChunker(max_tokens=512)
        merged_chunks = chunker.chunk(chunks)

        for i, merged in enumerate(merged_chunks):
            print(f"Chunk {i}:")
            print(merged["text"])
            print()

# Uncomment to test
test_semantic_chunker(kb_text)