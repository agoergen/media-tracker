import csv
import os
from app import db
from app.models import TheaterReference

def run_import_broadway():
    csv_path = 'app/backfill_data/broadway_data.csv'
    count = 0
    
    # Check if we've already imported
    if TheaterReference.query.first():
        print("TheaterReference already populated. Skipping import.")
        return 0

    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return 0

    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        # The CSV has an empty column at the start (index 0)
        reader = csv.DictReader(f)
        for row in reader:
            # ,Date_Close,Date_Open,Date_Previews,Intermission,Market,Prod_Type,Run_Time_Minutes,Run_Time_String,Run_Type,Show_Name,Show_Type,Theatre,Theatre_Address
            
            show_name = row.get('Show_Name')
            if not show_name:
                continue

            # Convert Run_Time_Minutes to int
            rtm = row.get('Run_Time_Minutes')
            try:
                rtm_int = int(float(rtm)) if rtm and rtm != '' else None
            except ValueError:
                rtm_int = None

            ref = TheaterReference(
                show_name=show_name,
                show_type=row.get('Show_Type'),
                theatre=row.get('Theatre'),
                date_open=row.get('Date_Open'),
                date_close=row.get('Date_Close'),
                run_time_minutes=rtm_int
            )
            db.session.add(ref)
            count += 1
            
    db.session.commit()
    print(f"Successfully imported {count} Broadway shows into reference table.")
    return count
