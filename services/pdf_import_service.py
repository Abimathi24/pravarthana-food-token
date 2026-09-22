import pdfplumber
import re
import uuid
import traceback
from services.firebase_service import add_participant

def process_pdf_import(file_path):
    extracted_data = []
    
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table[1:]:  # skip header row
                        if not row or len(row) < 6:
                            continue
                            
                        college = row[0].replace('\n', ' ').strip() if row[0] else "Unknown College"
                        dept = row[1].replace('\n', ' ').strip() if row[1] else "Unknown Dept"
                        
                        # Parse Members in columns 5, 6, 7, 8 (0-indexed)
                        for i in range(5, min(9, len(row))):
                            cell_text = row[i]
                            if not cell_text:
                                continue
                                
                            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', cell_text)
                            if email_match:
                                email = email_match.group(1).strip()
                                # Name is usually text before the email
                                name_part = cell_text[:email_match.start()].strip()
                                name = name_part.replace('\n', ' ')
                                
                                # Clean up some artifacts
                                name = re.sub(r'[^a-zA-Z\s\.]', '', name).strip()
                                
                                if not name:
                                    name = email.split('@')[0]
                                    
                                pid = "P" + str(uuid.uuid4())[:6].upper()
                                
                                extracted_data.append({
                                    "participant_id": pid,
                                    "name": name,
                                    "email": email,
                                    "college": college,
                                    "department": dept,
                                    "food_claimed": False
                                })
                                
    except Exception as e:
        print("PDF Parsing Error:", str(e))
        traceback.print_exc()
        return {"error": str(e)}
        
    inserted = 0
    errors = []
    for data in extracted_data:
        try:
            add_participant(data)
            inserted += 1
        except Exception as e:
            errors.append(str(e))
            print("Failed to add participant:", str(e))
            
    return {"inserted": inserted, "total_found": len(extracted_data), "errors": errors[:5]}
