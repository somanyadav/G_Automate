import pandas as pd
import PyPDF2
import google.generativeai as genai
import os
import json
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import time

# --- Configuration ---
CSV_FILE_NAME = "google_jobs_with_details.csv"
PDF_RESUME_FILE_NAME = "resume.pdf"  # Make sure to add your resume file

# --- !! IMPORTANT CONFIGS FOR FULL RUN !! ---
# These will be set as local variables in main() function
DEFAULT_USE_EMBEDDING_PRE_FILTERING = True
EMBEDDING_SIMILARITY_THRESHOLD = 0.55
MAX_JOBS_AFTER_EMBEDDING_FILTER = 200
MAX_JOBS_TO_ANALYZE_WITH_LLM = float('inf')

OUTPUT_CSV_NAME = "analyzed_google_jobs_full.csv"
SHORTLISTED_CSV_NAME = "shortlisted_google_jobs_full.csv"

# --- 1. Load API Key and Configure Google Generative AI ---
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY environment variable not found.")
    exit()

genai.configure(api_key=GOOGLE_API_KEY)

analysis_model = genai.GenerativeModel(model_name="gemini-1.5-flash")
embedding_model_name = "models/text-embedding-004"

# --- Caching ---
llm_response_cache = {}
CACHE_FILE = "llm_response_cache.json"

def load_cache():
    global llm_response_cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                llm_response_cache = json.load(f)
            print(f"Loaded {len(llm_response_cache)} items from cache.")
        except Exception as e:
            print(f"Could not load cache: {e}")
            llm_response_cache = {}
    else:
        llm_response_cache = {}

def save_cache():
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(llm_response_cache, f, indent=2)
    except Exception as e:
        print(f"Could not save cache: {e}")

# --- Helper Functions ---
def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            if not reader.pages:
                print(f"Warning: No pages found in PDF {pdf_path}.")
                return None
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            return text if text.strip() else None
    except Exception as e:
        print(f"Error extracting text from PDF {pdf_path}: {str(e)}")
        return None

def get_text_embedding(text_input, task_type="RETRIEVAL_DOCUMENT", title=None):
    try:
        if "text-embedding-004" in embedding_model_name:
            params = {'model': embedding_model_name, 'content': text_input}
            if title:
                params['title'] = title
            response = genai.embed_content(**params)
        elif "embedding-001" in embedding_model_name:
            response = genai.embed_content(model=embedding_model_name, content=text_input, task_type=task_type)
        else:
            response = genai.embed_content(model=embedding_model_name, content=text_input)
        return response['embedding']
    except Exception as e:
        print(f"Error generating embedding for text (len {len(text_input)}): {e}")
        time.sleep(1)
        try:
            if "text-embedding-004" in embedding_model_name:
                params = {'model': embedding_model_name, 'content': text_input}
                if title:
                    params['title'] = title
                response = genai.embed_content(**params)
            elif "embedding-001" in embedding_model_name:
                response = genai.embed_content(model=embedding_model_name, content=text_input, task_type=task_type)
            else:
                response = genai.embed_content(model=embedding_model_name, content=text_input)
            return response['embedding']
        except Exception as retry_e:
            print(f"Retry failed: {retry_e}")
            return None

def get_llm_assessment_json(resume_content, job_details_text, job_title_for_llm, job_url_for_llm):
    cache_key = job_url_for_llm
    if cache_key in llm_response_cache:
        return llm_response_cache[cache_key]

    prompt = f"""
    You are a highly skilled career advisor and resume analyst.
    Your task is to evaluate the provided resume against a specific job description and return your analysis strictly in JSON format.
    Also please make sure that The user has 2 years of experience. And is NOT focusing on core SDE roles. 

    **Resume Content:**
    ---
    {resume_content}
    ---

    **Job Description Details:**
    Job Title: {job_title_for_llm}
    Job URL: {job_url_for_llm}
    ---
    {job_details_text}
    ---

    **Instructions for JSON Output:**
    Please provide your analysis in a single JSON object with the following fields:
    - "job_title": (string) Echo back the job title provided.
    - "job_url": (string) Echo back the job URL provided.
    - "fit_score": (integer) A numerical score from 0 to 10 (inclusive). 10 is a perfect fit.
    - "fit_category": (string) One of: "Strong Fit", "Potential Fit", "Borderline Fit", "Not a Good Fit".
    - "key_matches": (array of strings) Specific skills/experiences from resume matching job requirements.
    - "potential_gaps": (array of strings) Specific skills/experiences from job description missing or less emphasized in resume.
    - "reasoning_summary": (string) A brief (2-3 sentences) justification for your fit_score and fit_category.
    - "auto_drafted_outreach_snippet": (string) A polite, concise, 2-sentence outreach message referencing one key match.

    Ensure the output is ONLY a valid JSON object. Do not include any text before or after the JSON.
    """
    try:
        response = analysis_model.generate_content(prompt)
        try:
            cleaned_response_text = response.text.strip()
            if cleaned_response_text.startswith("```json"):
                cleaned_response_text = cleaned_response_text[7:]
            if cleaned_response_text.endswith("```"):
                cleaned_response_text = cleaned_response_text[:-3]

            llm_output_json = json.loads(cleaned_response_text.strip())
            llm_response_cache[cache_key] = llm_output_json
            return llm_output_json
        except json.JSONDecodeError as je:
            error_detail = f"LLM response not valid JSON. JSONDecodeError: {je}. Response: {response.text[:500]}..."
            return {"error": error_detail, "job_title": job_title_for_llm, "job_url": job_url_for_llm}
        except AttributeError:
             error_detail = "Invalid LLM response object (no 'text' attribute)."
             return {"error": error_detail, "job_title": job_title_for_llm, "job_url": job_url_for_llm}
    except Exception as e:
        error_detail = f"LLM API call failed: {e}"
        return {"error": error_detail, "job_title": job_title_for_llm, "job_url": job_url_for_llm}

def main():
    """Main function"""
    # Set configuration as local variables to avoid scoping issues
    USE_EMBEDDING_PRE_FILTERING = DEFAULT_USE_EMBEDDING_PRE_FILTERING
    
    start_time = time.time()
    print("--- Starting Full Job Fit Analysis ---")
    load_cache()

    # 1. Extract Resume Content
    print(f"\nExtracting text from resume: {PDF_RESUME_FILE_NAME}...")
    if not os.path.exists(PDF_RESUME_FILE_NAME):
        print(f"Error: Resume file '{PDF_RESUME_FILE_NAME}' not found. Please add your resume file.")
        return
        
    resume_text = extract_text_from_pdf(PDF_RESUME_FILE_NAME)
    if not resume_text:
        print("Could not extract resume text. Exiting.")
        return
    print("Resume text extracted successfully.")
    
    resume_embedding = None
    if USE_EMBEDDING_PRE_FILTERING:
        print("Generating resume embedding...")
        resume_embedding = get_text_embedding(resume_text, task_type="RETRIEVAL_QUERY", title="Candidate Resume")
        if not resume_embedding:
            print("Could not generate resume embedding. Disabling embedding pre-filtering.")
            USE_EMBEDDING_PRE_FILTERING = False
        else:
            print("Resume embedding generated.")

    # 2. Load Job Data
    try:
        print(f"\nLoading job data from: {CSV_FILE_NAME}...")
        df_jobs_initial = pd.read_csv(CSV_FILE_NAME)
        if 'job_id_unique' not in df_jobs_initial.columns:
            df_jobs_initial['job_id_unique'] = df_jobs_initial.index.astype(str) + "_" + df_jobs_initial.get('url', pd.Series([''] * len(df_jobs_initial))).fillna('').str.split('=').str[-1]

    except FileNotFoundError:
        print(f"Error: CSV file '{CSV_FILE_NAME}' not found. Please run the job scraper first.")
        return
    print(f"Job data loaded successfully. Total jobs in CSV: {len(df_jobs_initial)}")

    # Define columns
    pref_qual_cols = [f'pref_qual_{i}' for i in range(1, 7)]
    responsibility_cols = [f'responsibility_{i}' for i in range(1, 6)]
    title_col = 'title'
    url_col = 'url'

    jobs_to_process_further_df = df_jobs_initial

    # 3. Embedding-Based Pre-filtering (if enabled)
    if USE_EMBEDDING_PRE_FILTERING and resume_embedding is not None:
        print("\n--- Starting Embedding Pre-filtering ---")
        job_embeddings_data = []
        print(f"Generating embeddings for {len(df_jobs_initial)} jobs (this may take a while)...")
        for i, (index, row) in enumerate(df_jobs_initial.iterrows()):
            job_title_for_embed = str(row.get(title_col, "")).strip()
            job_url_for_embed = str(row.get(url_col, f"job_index_{index}")).strip()

            pref_quals_list = [str(row.get(col, "")).strip() for col in pref_qual_cols if pd.notna(row.get(col)) and str(row.get(col)).strip()]
            resp_list = [str(row.get(col, "")).strip() for col in responsibility_cols if pd.notna(row.get(col)) and str(row.get(col)).strip()]

            job_desc_text_for_embedding = f"Preferred Qualifications: {' '.join(pref_quals_list)}\nResponsibilities: {' '.join(resp_list)}"

            if job_desc_text_for_embedding.strip():
                embedding = get_text_embedding(job_desc_text_for_embedding, title=job_title_for_embed)
                if embedding:
                    job_embeddings_data.append({'original_index': index, 'embedding': embedding, 'title': job_title_for_embed, 'url': job_url_for_embed})

            if (i + 1) % 50 == 0:
                print(f"  Generated embeddings for {i + 1}/{len(df_jobs_initial)} jobs...")
        print("Finished generating job embeddings.")

        if job_embeddings_data:
            job_embeddings_matrix = np.array([item['embedding'] for item in job_embeddings_data])
            similarities = cosine_similarity(np.array(resume_embedding).reshape(1, -1), job_embeddings_matrix)[0]

            for i, item in enumerate(job_embeddings_data):
                item['similarity'] = similarities[i]

            highly_similar_jobs_with_data = [item for item in job_embeddings_data if item['similarity'] >= EMBEDDING_SIMILARITY_THRESHOLD]
            highly_similar_jobs_with_data.sort(key=lambda x: x['similarity'], reverse=True)

            if len(highly_similar_jobs_with_data) > MAX_JOBS_AFTER_EMBEDDING_FILTER:
                highly_similar_jobs_with_data = highly_similar_jobs_with_data[:MAX_JOBS_AFTER_EMBEDDING_FILTER]

            if highly_similar_jobs_with_data:
                filtered_original_indices = [item['original_index'] for item in highly_similar_jobs_with_data]
                jobs_to_process_further_df = df_jobs_initial.loc[filtered_original_indices].copy()
                print(f"Embedding pre-filtering selected {len(jobs_to_process_further_df)} jobs for deeper LLM analysis.")
            else:
                print("No jobs met the embedding similarity threshold.")
                jobs_to_process_further_df = pd.DataFrame()
        else:
            print("Could not generate embeddings for any jobs.")
    else:
        print("\nSkipping embedding pre-filtering.")

    # 4. Apply MAX_JOBS_TO_ANALYZE_WITH_LLM cap
    if not jobs_to_process_further_df.empty:
        if len(jobs_to_process_further_df) > MAX_JOBS_TO_ANALYZE_WITH_LLM:
            final_jobs_for_llm_df = jobs_to_process_further_df.head(int(MAX_JOBS_TO_ANALYZE_WITH_LLM))
            print(f"\nCapping LLM analysis to the first {len(final_jobs_for_llm_df)} selected jobs due to MAX_JOBS_TO_ANALYZE_WITH_LLM.")
        else:
            final_jobs_for_llm_df = jobs_to_process_further_df
    else:
        final_jobs_for_llm_df = pd.DataFrame()

    print(f"\n--- LLM Analysis: Preparing to process {len(final_jobs_for_llm_df)} jobs ---")

    all_llm_assessments = []
    jobs_processed_count = 0

    for index, row in final_jobs_for_llm_df.iterrows():
        jobs_processed_count += 1
        job_title = str(row.get(title_col, "N/A")).strip()
        job_url = str(row.get(url_col, row.get('job_id_unique', f"fallback_id_{index}"))).strip()

        print(f"\n({jobs_processed_count}/{len(final_jobs_for_llm_df)}) Analyzing Job for LLM: {job_title}")

        pref_quals_list = [str(row.get(col, "")).strip() for col in pref_qual_cols if pd.notna(row.get(col)) and str(row.get(col)).strip()]
        resp_list = [str(row.get(col, "")).strip() for col in responsibility_cols if pd.notna(row.get(col)) and str(row.get(col)).strip()]

        job_pref_quals_text = "\n".join(f"- {item}" for item in pref_quals_list) if pref_quals_list else "Not specified."
        job_responsibilities_text = "\n".join(f"- {item}" for item in resp_list) if resp_list else "Not specified."

        job_details_for_llm = (
            f"Preferred Qualifications:\n{job_pref_quals_text}\n\n"
            f"Responsibilities:\n{job_responsibilities_text}"
        )

        assessment_json = get_llm_assessment_json(resume_text, job_details_for_llm, job_title, job_url)

        if 'error' in assessment_json:
            print(f"  ERROR for {job_title}: {assessment_json['error'][:200]}...")

        all_llm_assessments.append(assessment_json)

        # Save cache periodically
        if jobs_processed_count % 10 == 0:
            save_cache()

        time.sleep(0.5)

    save_cache()
    print("\nFinished LLM processing.")

    # 5. Post-Process, Filter, and Display/Save
    print("\n\n--- Final Results and Shortlist Generation ---")
    if not all_llm_assessments:
        print("No LLM assessments were generated.")
    else:
        enriched_assessments = []
        
        for i, assessment_result in enumerate(all_llm_assessments):
            original_row_data = {}
            if 'job_url' in assessment_result:
                matched_rows = df_jobs_initial[df_jobs_initial[url_col] == assessment_result['job_url']]
                if not matched_rows.empty:
                     original_row_data = matched_rows.iloc[0].to_dict()
                else:
                    matched_rows_id = df_jobs_initial[df_jobs_initial['job_id_unique'] == assessment_result['job_url']]
                    if not matched_rows_id.empty:
                        original_row_data = matched_rows_id.iloc[0].to_dict()

            combined_data = {**original_row_data, **assessment_result}
            enriched_assessments.append(combined_data)

        df_all_analyzed = pd.DataFrame(enriched_assessments)

        if not df_all_analyzed.empty:
            try:
                df_all_analyzed.to_csv(OUTPUT_CSV_NAME, index=False)
                print(f"\nAll analyzed job results saved to: {OUTPUT_CSV_NAME}")
            except Exception as e:
                print(f"Error saving all analyzed jobs CSV: {e}")

        if 'error' in df_all_analyzed.columns:
            df_successful_assessments = df_all_analyzed[~df_all_analyzed['error'].notna() & df_all_analyzed['fit_score'].notna()].copy()
        else:
            df_successful_assessments = df_all_analyzed[df_all_analyzed['fit_score'].notna()].copy()

        if not df_successful_assessments.empty:
            print(f"\nTotal successful LLM assessments: {len(df_successful_assessments)}")

            df_successful_assessments['fit_score'] = pd.to_numeric(df_successful_assessments['fit_score'], errors='coerce')
            df_successful_assessments.dropna(subset=['fit_score'], inplace=True)
            df_successful_assessments['fit_score'] = df_successful_assessments['fit_score'].astype(int)

            desired_fit_score_threshold = 7
            desired_categories = ["Strong Fit", "Potential Fit"]

            shortlisted_jobs_df = df_successful_assessments[
                (df_successful_assessments['fit_score'] >= desired_fit_score_threshold) &
                (df_successful_assessments['fit_category'].isin(desired_categories))
            ].copy()

            if not shortlisted_jobs_df.empty:
                shortlisted_jobs_df.sort_values("fit_score", ascending=False, inplace=True)
                print(f"\n--- Shortlisted Jobs (Score >= {desired_fit_score_threshold}) ---")
                for _, job_row in shortlisted_jobs_df.head(10).iterrows():
                    print(f"\nJob Title: {job_row['job_title']}")
                    print(f"URL: {job_row['job_url']}")
                    print(f"Fit Score: {job_row.get('fit_score', 'N/A')}/10")
                    print(f"Fit Category: {job_row.get('fit_category', 'N/A')}")
                    
                    key_matches_list = job_row.get('key_matches', [])
                    potential_gaps_list = job_row.get('potential_gaps', [])
                    print(f"Key Matches: {', '.join(key_matches_list) if isinstance(key_matches_list, list) else 'N/A'}")
                    print(f"Potential Gaps: {', '.join(potential_gaps_list) if isinstance(potential_gaps_list, list) else 'N/A'}")
                    print(f"Outreach Snippet: {job_row.get('auto_drafted_outreach_snippet', 'N/A')}")
                    print("-" * 30)

                try:
                    shortlisted_jobs_df.to_csv(SHORTLISTED_CSV_NAME, index=False)
                    print(f"\nShortlisted jobs ({len(shortlisted_jobs_df)}) saved to: {SHORTLISTED_CSV_NAME}")
                except Exception as e:
                    print(f"Error saving shortlisted jobs CSV: {e}")

            else:
                print(f"\nNo jobs met the shortlisting criteria.")
        else:
            print("\nNo successful LLM assessments to create a shortlist from.")

    end_time = time.time()
    total_time = end_time - start_time
    print(f"\n--- Analysis Complete in {total_time:.2f} seconds ({total_time/60:.2f} minutes) ---")

if __name__ == "__main__":
    main()
