# ⚖️ Tradeoffs & Architecture Choices

Building a robust, AI-driven pediatric safety agent within a 5-hour time constraint required specific architectural and product decisions. Below are the core tradeoffs made during development.

### 1. Problem Selection
* **The Choice:** I chose to build a deterministic safety layer (RAG policy matching) over standard AI product recommendations. 
* **The "Why":** E-commerce personalization is an easily solved problem; *safe* pediatric personalization is high-leverage. Recommending the wrong toy to a 6-month-old isn't just a bad user experience; it is a serious brand liability. 

### 2. Model & Architecture Choice
* **The Choice:** A multi-agent LangGraph architecture over a single mega-prompt.
* **The "Why":** This heavily separates concerns: Vision (sees) -> Curator (searches) -> Auditor (protects) -> Explainer (localizes). This allows for easier debugging, distinct model routing, and isolated unit testing (like my `run_evals.py` script).

### 3. Handling Uncertainty
The system is explicitly designed to handle uncertainty in two ways:
1. **Catalog Misses:** If the ChromaDB search returns no safe matches for a specific milestone, the Curator agent returns an empty array `[]` rather than hallucinating fake products.
2. **Contextual Vetoes:** The Safety Agent dynamically vetoes products based on environmental context (e.g., actively flagging a walker if the Vision Agent detects a cluttered room in the image).

### 4. What I Cut
I initially intended to scrape Mumzworld's actual catalog for live data. However, due to the assignment's time constraints and the directive to "generate your own data," I chose to seed a local ChromaDB with 5 synthetic products and 2 strict GCC pediatric safety rules.

### 5. What I Would Build Next
* **UI Integration:** A simple frontend interface to drag-and-drop images.
* **Expanded Knowledge Base:** Expanding the vector database to ingest standard GCC pediatric safety guidelines directly from PDF documents, allowing the Safety Agent to audit hundreds of edge-case hazards automatically.