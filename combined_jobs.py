import pandas as pd  # For handling data tables
import re            # For cleaning text
import uuid          # To assign unique IDs to jobs
df1 = pd.read_csv("C:\project 2.1\job_recommender\data\data_science_canada_march_2024.csv")
df2 = pd.read_csv("C:\project 2.1\job_recommender\data\linkedin_canada.csv")

#Normalize column names

def normalize_columns(df):
    mapping = {
        'company': 'companyName',
        'company_name': 'companyName',
        'companyname': 'companyName',
        'worktype': 'workType',
        'contracttype': 'contractType',
        'experience': 'experienceLevel',
        'applications': 'applicationsCount',
        'applications_count': 'applicationsCount',
        'url': 'jobUrl',
        'job_url': 'jobUrl',
        'posted_date': 'postedDate'
    }
    df = df.rename(columns={c: mapping.get(c, c) for c in df.columns})
    return df
#Select Relevant Columns

def select_relevant_columns(df):
    wanted = [
        'title', 'description', 'companyName', 'location',
        'experienceLevel', 'sector', 'workType', 'contractType',
        'applicationsCount', 'jobUrl', 'postedDate'
    ]
    for col in wanted:
        if col not in df.columns:
            df[col] = None
    return df[wanted]

#clean the data
def clean_data(df):
    # Clean text columns
    text_cols = ['title', 'companyName', 'location', 'experienceLevel',
                 'sector', 'workType', 'contractType', 'jobUrl']
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()
        df[col].replace({'nan': None, 'NaN': None, 'None': None}, inplace=True)
    
    # Convert application counts to numbers
    def extract_number(x):
        if pd.isna(x):
            return 0
        match = re.search(r'(\d[\d,]*)', str(x))
        return int(match.group(1).replace(',', '')) if match else 0

    df['applicationsCount'] = df['applicationsCount'].apply(extract_number).astype(int)
    
    # Parse dates
    df['postedDate'] = pd.to_datetime(df['postedDate'], errors='coerce').dt.date
    
    # Remove duplicates
    df.drop_duplicates(subset=['title', 'companyName', 'location', 'jobUrl'], inplace=True)
    
    # Add job_id column
    df.insert(0, 'job_id', [str(uuid.uuid4()) for _ in range(len(df))])
    
    return df
#Merge and save
def combine_and_clean():
    # Load both files
    df1 = normalize_columns(pd.read_csv("C:\project 2.1\job_recommender\data\data_science_canada_march_2024.csv"))
    df2 = normalize_columns(pd.read_csv("C:\project 2.1\job_recommender\data\linkedin_canada.csv"))

    # Select only important columns
    df1 = select_relevant_columns(df1)
    df2 = select_relevant_columns(df2)

    # Merge them
    combined = pd.concat([df1, df2], ignore_index=True)

    # Clean and finalize
    combined = clean_data(combined)

    # Save the cleaned dataset
    combined.to_csv("combined_jobs.csv", index=False)
    print(f"✅ Saved {len(combined)} clean job listings to combined_jobs.csv")

    return combined
if __name__ == "__main__":
    combined = combine_and_clean()
    print(combined.head(10))
