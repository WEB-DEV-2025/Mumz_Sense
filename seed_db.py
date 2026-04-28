import database

def seed_catalog():
    print("📦 Seeding Mumzworld Catalog...")
    catalog_db = database.get_catalog_db()
    
    # We include a mix of safe products and intentionally UNSAFE products
    products = [
        {
            "id": "PROD_001",
            "description": "Premium Soft Foam Playmat. Perfect for babies learning to crawl. Non-toxic and thick.",
            "activity": "crawling for 6-12 month olds"
        },
        {
            "id": "PROD_002",
            "description": "Silicone Teething Ring. BPA-free, single solid piece of medical-grade silicone.",
            "activity": "teething for 3-6 month olds"
        },
        {
            "id": "PROD_003",
            "description": "Amber Teething Necklace with small loose beads. Aesthetic and traditional.",
            "activity": "teething for 3-6 month olds" # Intentionally UNSAFE for this age
        },
        {
            "id": "PROD_004",
            "description": "Wooden Activity Walker with sturdy wheels and locking mechanism.",
            "activity": "walking for 9-18 month olds"
        },
        {
            "id": "PROD_005",
            "description": "Plush Sleep Sack, 1.0 TOG. Replaces loose blankets in the crib.",
            "activity": "sleeping for 0-6 month olds"
        }
    ]
    
    ids = [p["id"] for p in products]
    documents = [p["description"] for p in products]
    
    catalog_db.upsert(
        ids=ids,
        documents=documents
    )
    print(f"✅ Added {len(products)} products to the catalog database.")

def seed_safety_rules():
    print("🛡️ Seeding Safety Policies...")
    safety_db = database.get_safety_db()
    
    rules = [
        {
            "id": "RULE_001",
            "policy": "Items for children under 3 years old MUST NOT contain loose beads, small parts, or long strings due to extreme choking and strangulation hazards."
        },
        {
            "id": "RULE_002",
            "policy": "Sleep environments for infants under 1 year must not contain loose blankets, pillows, or bumper pads."
        }
    ]
    
    ids = [r["id"] for r in rules]
    documents = [r["policy"] for r in rules]
    
    safety_db.upsert(
        ids=ids,
        documents=documents
    )
    print(f"✅ Added {len(rules)} safety rules to the policy database.")

if __name__ == "__main__":
    print("🚀 Initializing Database Seeding...")
    seed_catalog()
    seed_safety_rules()
    print("🎉 Database is ready! You can now run your LangGraph agents.")