import pandas as pd
import numpy as np

# Load your dataset
df = pd.read_csv("data/combined_jobs.csv")

# Clean empty or NaN text fields
for col in ['title', 'description', 'sector', 'experienceLevel']:
    if col in df.columns:
        df[col] = df[col].fillna("")

# Add a function to generate job-related text automatically
def generate_description(title):
    title = title.lower()
    if "data scientist" in title:
        return "Data Scientist skilled in Python, SQL, Machine Learning, Deep Learning, TensorFlow, Keras, Scikit-learn, Pandas, and Power BI."
    elif "machine learning" in title:
        return "Machine Learning Engineer experienced with model training, neural networks, Python, TensorFlow, PyTorch, and cloud platforms like AWS or Azure."
    elif "data analyst" in title:
        return "Data Analyst proficient in SQL, Excel, Tableau, Power BI, and data visualization, with experience cleaning and analyzing large datasets."
    elif "business analyst" in title:
        return "Business Analyst skilled in stakeholder analysis, Excel, Power BI, data-driven decision making, and business process improvement."
    elif "ai engineer" in title or "artificial intelligence" in title:
        return "AI Engineer working on deep learning, computer vision, and natural language processing projects using Python, TensorFlow, and PyTorch."
    elif "developer" in title or "software engineer" in title:
        return "Software Developer with experience in Python, Java, JavaScript, REST APIs, and agile development."
    elif "data engineer" in title:
        return "Data Engineer experienced with ETL pipelines, SQL, Big Data tools like Spark, Hadoop, and cloud data warehouses."
    else:
        return "Professional experienced in Python, SQL, data analysis, and reporting."

# Fill missing descriptions
df['description'] = np.where(
    df['description'].str.strip() == "",
    df['title'].apply(generate_description),
    df['description']
)

# Add a combined text field for TF-IDF (optional)
def safe(x): return '' if pd.isna(x) else str(x)
df['text'] = (
    df['title'].map(safe) + ' ' +
    df['description'].map(safe) + ' ' +
    df['sector'].map(safe) + ' ' +
    df['experienceLevel'].map(safe) + ' ' +
    df['companyName'].map(safe) + ' ' +
    df['location'].map(safe)
).str.lower()
# Replace newlines and multiple spaces with commas
df['description'] = df['description'].replace(r'[\r\n]+', ', ', regex=True)
df['description'] = df['description'].replace(r'\s{2,}', ' ', regex=True)

# Save the enriched dataset
df.to_csv("data/combined_jobs_enriched.csv", index=False)
print("✅ Enriched dataset saved as data/combined_jobs_enriched.csv")
