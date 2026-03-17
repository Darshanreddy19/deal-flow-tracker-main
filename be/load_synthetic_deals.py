"""
Load synthetic deal data into Qdrant.
This script reads synthetic_data.json and upserts all deal records to Qdrant.
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from qdrant_service import upsert_text, ensure_collection

load_dotenv()

def load_and_upsert_synthetic_deals():
    """Load synthetic deals from JSON and upsert to Qdrant."""

    # Ensure collection exists
    ensure_collection()

    # Read synthetic data
    data_path = Path(__file__).parent / "data" / "synthetic_data.json"

    if not data_path.exists():
        print(f"❌ Error: {data_path} not found")
        return

    with open(data_path, 'r') as f:
        deals = json.load(f)

    print(f"📊 Found {len(deals)} deals in synthetic_data.json")

    # Upsert each deal to Qdrant
    for deal in deals:
        # Create a searchable text representation
        text_content = f"""
Deal ID: {deal['deal_id']}
Sector: {deal['sector']}
Client: {deal['parties']['client']}
Supplier: {deal['parties']['supplier']}
Specialist: {deal['parties']['specialist']}
Status: {deal['status']}
Bottleneck: {deal['bottleneck']}
Actions: {', '.join(deal['action_items'])}
Communication: {[f"{c['sender']}: {c['content']}" for c in deal['communication_history']]}
        """.strip()

        # Prepare metadata
        metadata = {
            "deal_id": deal['deal_id'],
            "sector": deal['sector'],
            "client": deal['parties']['client'],
            "supplier": deal['parties']['supplier'],
            "specialist": deal['parties']['specialist'],
            "status": deal['status'],
            "bottleneck": deal['bottleneck'],
            "action_items": json.dumps(deal['action_items']),
            "communication_history": json.dumps(deal['communication_history']),
            "num_messages": len(deal['communication_history']),
        }

        # Upsert to Qdrant
        point_id = upsert_text(text_content, metadata)
        print(f"✅ Upserted {deal['deal_id']} (ID: {point_id})")

    print(f"\n🎉 Successfully upserted {len(deals)} deals to Qdrant!")

if __name__ == "__main__":
    load_and_upsert_synthetic_deals()
