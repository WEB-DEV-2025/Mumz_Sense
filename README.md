# Mumz-Sense: AI Pediatric Safety & Curation Agent 🍼

**🎥 [Watch the 3-Minute Live Demo on Loom](https://drive.google.com/file/d/1w84rt797b_-KxPfWedvNPu71Tw-Od9pp/view?usp=drivesdk)**

## 🌟 What is Mumz-Sense?
Mumz-Sense is a multi-agent AI pipeline designed to act as an automated safety auditor for pediatric e-commerce. Instead of just recommending baby products, it prioritizes safety by doing the following:
1. **Context Analysis:** A Vision Agent analyzes an image of a child to determine their age, activity, and environmental hazards.
2. **Catalog Retrieval:** A Curator Agent fetches candidate products from a local ChromaDB catalog.
3. **Safety Auditing:** A Safety Agent cross-references the products and the child's context against strict GCC pediatric safety policies, actively vetoing dangerous items (e.g., choking or tripping hazards).
4. **Bilingual Explanations:** An Explainer Agent outputs a final JSON with localized Khaleeji Arabic and English reasoning for why the approved products are safe.


## Setup Instructions (Under 5 Minutes)
1. Clone this repository.
2. Create a virtual environment: `python -m venv .venv`
3. Activate it: `.\.venv\Scripts\activate` (Windows)
4. Install dependencies: `python -m pip install -r requirements.txt`
5. Add your `.env` file with `OPENROUTER_API_KEY=your_key` and `GEMINI_API_KEY=your_key`
6. Run database seed: `python seed_db.py`
7. Run the pipeline: `python main.py`


**Time Log:**
* **Total Time:** ~4.5 hours (Did not exceed the 5-hour limit).
* **Phase 1 (1 hr):** Architecture design, LangGraph state setup, and seeding local ChromaDB with synthetic catalog/safety rules.
* **Phase 2 (1.5 hrs):** Core agent implementation, crafting strict safety auditor prompts, and OpenRouter API integration.
* **Phase 3 (1 hr):** Debugging API rate limits, refactoring the vision node to use base64 encoding, and fixing model auto-routing.
* **Phase 4 (1 hr):** Building the automated eval script (`run_evals.py`), analyzing test cases, writing the README, and recording the Loom.


## Tooling & Provenance
I used a heavy AI-assisted workflow to architect and debug this pipeline in under 5 hours.
* **AI Assistant (Pair-Programming):** Gemini 3.1 Pro (via Google AI Studio/Web). Used for conceptualizing the LangGraph architecture, debugging Windows-specific Python environment issues, and formatting the ChromaDB vector queries. 
* **Model Harness:** OpenRouter. I chose OpenRouter to unify my Vision and Text models under one API, bypassing rate limits.
* **Models Used:** * `openrouter/free` (Auto-routed to Llama 3.2 11B Vision for image analysis).
  * `openrouter/free` (Auto-routed to Llama 3/Mistral class models for curation, safety audits, and bilingual JSON generation).
* **Where I Stepped In:** Initially, I attempted to use Google's `gemini-2.0-flash` for the vision node, but encountered strict Free Tier rate limits (`429 RESOURCE_EXHAUSTED`). I manually intervened, refactored the image to a base64 encoded string, and swapped the entire pipeline to OpenRouter's auto-routing endpoints to guarantee 100% uptime for this demo.
* **Key System Prompt:** The Safety Agent's prompt is the core of this project. It forces the LLM to act as a strict auditor: *"You are a child safety auditor... Is this product SAFE for this child? Respond with a JSON object: {"verdict": "approved" or "vetoed", "reason": "brief explanation"}."*


## Evals & Rigor
To ensure production quality and prove that the Safety Agent does not hallucinate, I built an automated evaluation script (`run_evals.py`). This script bypasses the Vision node to isolate the Safety Node, testing it against the entire database using controlled variables.
* **Rubric:**
  * **Pass:** Correctly identifies safe products AND accurately flags unsafe products based on retrieved ChromaDB safety policies.
  * **Fail:** Approves a dangerous product or hallucinates a safety rule.
* **Test Cases:** I ran 10 automated test cases evaluating the database across two distinct scenarios:
  1. **Test Suite A:** Profile = "6-12 months, teething and crawling"
  2. **Test Suite B:** Profile = "0-6 months, sleeping"
* **Results:** **10/10 Score**. The RAG architecture completely eliminated safety hallucinations. It consistently approved context-safe items (e.g., playmats, sleep sacks) and accurately vetoed items violating safety policies (e.g., explicitly flagging the amber teething necklace due to the under-3 loose bead choking hazard rule).


## Tradeoffs & Architecture Choice
* **Why this problem?** E-commerce personalization is easy; *safe* pediatric personalization is high-leverage. A wrong recommendation for a 6-month-old isn't just bad UX; it's a liability. I chose to build a deterministic safety layer (RAG policy matching) over standard AI recommendations.
* **Model Choice:** I opted for a multi-agent LangGraph architecture over a single mega-prompt. This separates concerns: Vision (sees) -> Curator (searches) -> Auditor (protects) -> Explainer (localizes).
* **Handling Uncertainty:** The system is explicitly designed to handle uncertainty in two ways:
  1. If the ChromaDB search returns no safe matches for a specific milestone, the Curator agent returns an empty array `[]` rather than hallucinating products.
  2. The Safety Agent defaults to "Vetoed" if the safety rules conflict with the product description (e.g., flagging an amber teething necklace due to loose beads).
* **What I Cut:** I initially wanted to scrape Mumzworld's actual catalog, but due to the time constraints and assignment rules, I seeded a local ChromaDB with 5 synthetic products and 2 strict GCC safety rules.
* **What I'd Build Next:** A UI to drag-and-drop images, and expanding the vector database to ingest standard GCC pediatric safety guidelines directly from PDF documents.