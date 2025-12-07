# recommender.py
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Recommender:
    def __init__(self, data_path='data/combined_jobs_enriched.csv'):
        # Load dataset
        self.df = pd.read_csv(data_path)

        # 1️⃣ Prepare text column for vectorization
        def safe(x): return '' if pd.isna(x) else str(x)
        import re

        def clean_text(x):
            x = str(x).lower()
            x = re.sub(r"[^a-z0-9\s]", " ", x)
            return x

        # Combine + add fallback keywords if description is empty
        self.df['text'] = (
            self.df['title'].map(safe) + ' ' +
            self.df['description'].map(safe) + ' ' +
            self.df['sector'].map(safe) + ' ' +
            self.df['experienceLevel'].map(safe) + ' ' +
            self.df['companyName'].map(safe) + ' ' +
            self.df['workType'].map(safe) + ' ' +
            self.df['contractType'].map(safe) + ' ' +
            self.df['location'].map(safe)
        ).apply(clean_text)

        # Add synthetic keywords for empty descriptions
        self.df['text'] = self.df['text'].apply(
            lambda t: t if len(t.strip()) > 30 else t + ' data science python analytics machine learning sql dashboard'
        )

        # 2️⃣ Create TF-IDF matrix
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=100000,
            ngram_range=(1, 3),
            min_df=1
        )

        self.matrix = self.vectorizer.fit_transform(self.df['text'])

        
        print("✅ TF-IDF matrix shape:", self.matrix.shape)

        # 3️⃣ Normalize popularity (applicationsCount)
        pop = pd.to_numeric(self.df.get('applicationsCount', 0), errors='coerce').fillna(0)
        if pop.max() > 0:
            pop_norm = (np.log1p(pop) - np.log1p(pop).min()) / (np.log1p(pop).max() - np.log1p(pop).min())
        else:
            pop_norm = np.zeros(len(pop))
        self.df['popularity'] = pop_norm

        # 4️⃣ Weight parameters
        self.alpha = 0.7   # content weight
        self.beta = 0.3    # popularity weight

    # -----------------------------
    # Core Recommendation Function
    # -----------------------------
    def recommend_text(self, text, top_n=10, location=None, experience=None):
        """
        text: user query or resume text
        location: optional location filter
        experience: optional experience filter
        """
        if not text or not str(text).strip():
            return []

        # Compute similarity
        query_vec = self.vectorizer.transform([text.lower()])
        sim_scores = cosine_similarity(query_vec, self.matrix).flatten()

        # Hybrid score
        hybrid_score = self.alpha * sim_scores + self.beta * self.df['popularity'].values

        # Sort indices
        top_idx = np.argsort(-hybrid_score)
        results = []

        # Keep track of max similarity (for scaling match%)
        max_sim = sim_scores.max() if sim_scores.max() > 0 else 1e-6

        for i in top_idx:
            row = self.df.iloc[i]
            # Optional filters
            if location and isinstance(row.get('location'), str):
                if location.lower() not in row['location'].lower():
                    continue
            if experience and isinstance(row.get('experienceLevel'), str):
                if experience.lower() not in row['experienceLevel'].lower():
                    continue

            sim_percent = round((sim_scores[i] / max_sim) * 100, 1)

            results.append({
                'title': row.get('title', ''),
                'companyName': row.get('companyName', ''),
                'location': row.get('location', ''),
                'experienceLevel': row.get('experienceLevel', ''),
                'description': row.get('description', ''),
                'jobUrl': row.get('jobUrl', ''),
                'matchScore': sim_percent
            })

            if len(results) >= top_n:
                break

        #  Fallback: show top jobs if none matched
        if not results:
            print("⚠️ No strong match — showing fallback jobs.")
            fallback = self.df.sort_values('popularity', ascending=False).head(top_n)
            for _, row in fallback.iterrows():
                results.append({
                    'title': row.get('title', ''),
                    'companyName': row.get('companyName', ''),
                    'location': row.get('location', ''),
                    'experienceLevel': row.get('experienceLevel', ''),
                    'description': row.get('description', ''),
                    'jobUrl': row.get('jobUrl', ''),
                    'matchScore': 0
                })

        return results
