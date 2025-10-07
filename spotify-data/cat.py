import json
import os
from pathlib import Path

def combine_json_files():
    current_dir = Path(__file__).parent
    combined_data = []
    
    json_files = list(current_dir.glob("*.json"))
    
    if not json_files:
        print("No JSON files found in the current directory")
        return
    
    print(f"Found {len(json_files)} JSON files to combine:")
    
    for json_file in sorted(json_files):
        print(f"Processing: {json_file.name}")
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                if isinstance(data, list):
                    combined_data.extend(data)
                    print(f"  Added {len(data)} items from {json_file.name}")
                else:
                    combined_data.append(data)
                    print(f"  Added 1 item from {json_file.name}")
                    
        except json.JSONDecodeError as e:
            print(f"  Error reading {json_file.name}: {e}")
        except Exception as e:
            print(f"  Unexpected error with {json_file.name}: {e}")
    
    output_file = current_dir / "combined_data.json"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nSuccessfully combined {len(combined_data)} total items")
        print(f"Output saved to: {output_file}")
        
    except Exception as e:
        print(f"Error writing combined file: {e}")

if __name__ == "__main__":
    combine_json_files()