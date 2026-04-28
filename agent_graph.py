import os
import json
import re
import base64
import PIL.Image
from openai import OpenAI
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from schemas import MilestoneExtraction, ProductRecommendation
import database
from dotenv import load_dotenv
load_dotenv()

# --- 1. API Configurations ---

# Configure OpenRouter (Handles BOTH Text and Vision now!)
or_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY")
)
TEXT_MODEL = "openrouter/free"
VISION_MODEL = "openrouter/free"


# --- 2. State & Helpers ---
class MumzState(TypedDict):
    input_image_path: str
    extracted_milestone: MilestoneExtraction | None
    curated_products: List[Dict[str, Any]]
    vetoed_products: List[Dict[str, Any]]
    approved_products: List[Dict[str, Any]]
    final_output: List[ProductRecommendation]

def extract_json_from_text(text: str) -> str:
    """Helper to clean markdown formatting from LLM JSON outputs."""
    text = text.strip()
    
    # We use string multiplication to create the backticks safely
    # This prevents markdown parsers from breaking the string
    marker = "`" * 3
    pattern = rf"{marker}(?:json)?\s*(.*?)\s*{marker}"
    
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1)
    
    # If no formatting is found, assume the text is already raw JSON
    return text

# --- 3. Agent Nodes ---

def vision_agent(state: MumzState) -> dict:
    """
    Node 1: Uses Llama Vision via OpenRouter to analyze the child's image.
    """
    print("\n👁️  [Vision Agent] Analyzing image with Llama Vision...")
    
    image_path = state["input_image_path"]
    
    # Convert the image to base64 so OpenRouter can read it
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')
    
    prompt = """You are a pediatric development expert. Analyze this image of a child and return a JSON object with these exact keys:
- "age_estimate": The estimated age range of the child (e.g., "6-9 months", "1-2 years").
- "detected_activity": The developmental activity the child is engaged in (e.g., "crawling", "standing with support", "playing with blocks").
- "safety_hazards": A JSON array of potential safety hazards visible in the environment (e.g., ["sharp table corners", "uncovered electrical outlets"]). Return an empty array [] if none are found.

Return ONLY the JSON object, no other text."""

    response = or_client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    )
    
    raw_json = extract_json_from_text(response.choices[0].message.content)
    data = json.loads(raw_json)
    milestone = MilestoneExtraction(**data)
    
    print(f"   ✅ Age: {milestone.age_estimate}, Activity: {milestone.detected_activity}")
    print(f"   ⚠️  Hazards: {milestone.safety_hazards}")
    
    return {"extracted_milestone": milestone}


def curator_agent(state: MumzState) -> dict:
    """
    Node 2: Uses ChromaDB to find relevant products based on the
    extracted milestone, then asks LLM to curate the best matches.
    """
    print("\n🛒 [Curator Agent] Finding products...")
    
    milestone = state["extracted_milestone"]
    search_query = f"Products for a {milestone.age_estimate} old child who is {milestone.detected_activity}"
    
    # Retrieve candidate products from ChromaDB
    candidates = database.query_products(search_query, n_results=5)
    
    if not candidates:
        print("   ⚠️  No products found in catalog. Returning empty list.")
        return {"curated_products": []}
    
    prompt = f"""You are a product curator for a baby & children's e-commerce store.

A child has been identified with the following profile:
- Age: {milestone.age_estimate}
- Activity: {milestone.detected_activity}
- Safety Hazards: {json.dumps(milestone.safety_hazards)}

Here are the candidate products from our catalog:
{json.dumps(candidates, indent=2)}

Select the TOP 3 most relevant products for this child's developmental stage. Return a JSON array of objects, each with:
- "id": the product id
- "description": the product description
- "metadata": the product metadata

Return ONLY the JSON array, no other text."""

    response = or_client.chat.completions.create(
        model=TEXT_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    
    raw_json = extract_json_from_text(response.choices[0].message.content)
    curated = json.loads(raw_json)
    
    print(f"   ✅ Curated {len(curated)} products.")
    return {"curated_products": curated}


def safety_agent(state: MumzState) -> dict:
    """
    Node 3: Checks each curated product against safety policies
    in ChromaDB and vetoes any that are unsafe.
    """
    print("\n🛡️  [Safety Agent] Running safety audit...")
    
    milestone = state["extracted_milestone"]
    curated = state["curated_products"]
    approved = []
    vetoed = []
    
    for product in curated:
        desc = product.get("description", "")
        # Retrieve relevant safety rules for this product
        safety_rules = database.query_safety_rules(desc, n_results=2)
        
        prompt = f"""You are a child safety auditor. Given the following:

Child Profile:
- Age: {milestone.age_estimate}
- Activity: {milestone.detected_activity}
- Environmental Hazards: {json.dumps(milestone.safety_hazards)}

Product: {json.dumps(product)}

Relevant Safety Rules:
{json.dumps(safety_rules)}

Is this product SAFE for this child? Respond with a JSON object:
{{"verdict": "approved" or "vetoed", "reason": "brief explanation"}}

Return ONLY the JSON object."""

        response = or_client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        
        raw_json = extract_json_from_text(response.choices[0].message.content)
        result = json.loads(raw_json)
        
        if result.get("verdict") == "approved":
            product["safety_reason"] = result.get("reason", "")
            approved.append(product)
            print(f"   ✅ Approved: {product.get('id', 'unknown')}")
        else:
            product["safety_reason"] = result.get("reason", "")
            vetoed.append(product)
            print(f"   ❌ Vetoed: {product.get('id', 'unknown')} — {result.get('reason', '')}")
    
    return {"approved_products": approved, "vetoed_products": vetoed}


def explainer_agent(state: MumzState) -> dict:
    """
    Node 4: Generates bilingual (EN/AR) reasoning for each approved
    product and builds the final ProductRecommendation output.
    """
    print("\n📝 [Explainer Agent] Generating recommendations...")
    
    milestone = state["extracted_milestone"]
    approved = state["approved_products"]
    recommendations = []
    
    for product in approved:
        prompt = f"""You are a bilingual (English/Arabic) parenting advisor.

A child (age: {milestone.age_estimate}, activity: {milestone.detected_activity}) has been matched with this product:
{json.dumps(product)}

Generate a JSON object with:
- "product_id": "{product.get('id', '')}"
- "reasoning_en": A 2-3 sentence explanation in English of why this product is good for this child.
- "reasoning_ar": The same explanation translated into Arabic.
- "safety_audit_status": "passed"

Return ONLY the JSON object."""

        response = or_client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        
        raw_json = extract_json_from_text(response.choices[0].message.content)
        data = json.loads(raw_json)
        rec = ProductRecommendation(**data)
        recommendations.append(rec)
        print(f"   ✅ Recommendation ready for: {rec.product_id}")
    
    return {"final_output": recommendations}

# --- 4. Build the Graph ---

workflow = StateGraph(MumzState)

# Add nodes
workflow.add_node("vision_agent", vision_agent)
workflow.add_node("curator_agent", curator_agent)
workflow.add_node("safety_agent", safety_agent)
workflow.add_node("explainer_agent", explainer_agent)

# Define the linear pipeline
workflow.set_entry_point("vision_agent")
workflow.add_edge("vision_agent", "curator_agent")
workflow.add_edge("curator_agent", "safety_agent")
workflow.add_edge("safety_agent", "explainer_agent")
workflow.add_edge("explainer_agent", END)

# Compile the graph
mumz_sense_graph = workflow.compile()