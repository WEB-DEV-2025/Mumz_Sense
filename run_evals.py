import json
import database
from agent_graph import or_client, TEXT_MODEL, extract_json_from_text

def run_all_products_eval():
    print("🧪 Starting Automated Evals on ALL Products...\n")
    
    # 1. Get EVERY product from the database
    catalog_db = database.get_catalog_db()
    all_data = catalog_db.get()
    
    # 2. Define our Test Subject (A 6-month-old teething baby)
    test_age = "6-12 months"
    test_activity = "teething and crawling"
    
    print(f"👶 Test Profile: {test_age}, Activity: {test_activity}\n")
    print("-" * 70)
    print(f"{'Product ID':<12} | {'Status':<10} | {'Reasoning'}")
    print("-" * 70)

    # 3. Loop through every product and run the Safety Agent
    for i in range(len(all_data['ids'])):
        product = {
            "id": all_data['ids'][i],
            "description": all_data['documents'][i]
        }
        
        # Get safety rules for this specific product
        safety_rules = database.query_safety_rules(product['description'], n_results=2)
        
        prompt = f"""You are a child safety auditor. 
        Child Age: {test_age}
        Activity: {test_activity}
        Product: {json.dumps(product)}
        Rules: {json.dumps(safety_rules)}
        
        Is this product SAFE for this child? Respond with a JSON object:
        {{"verdict": "approved" or "vetoed", "reason": "brief explanation"}}
        Return ONLY the JSON object."""

        try:
            response = or_client.chat.completions.create(
                model=TEXT_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            
            raw_json = extract_json_from_text(response.choices[0].message.content)
            result = json.loads(raw_json)
            
            verdict = result.get("verdict", "error").upper()
            status_icon = "✅" if verdict == "APPROVED" else "❌"
            
            print(f"{product['id']:<12} | {status_icon} {verdict:<7} | {result.get('reason')}")
            
        except Exception as e:
            print(f"{product['id']:<12} | ⚠️ ERROR    | API Rate limit or failure")

    print("-" * 70)
    print("\n🎉 Evals Complete! Copy this output for your README.")

if __name__ == "__main__":
    run_all_products_eval()