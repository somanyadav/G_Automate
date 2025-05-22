import aiohttp
from bs4 import BeautifulSoup
import csv
import time
import os
from urllib.parse import urljoin
import re
import pandas as pd
import asyncio

# Number of concurrent requests
CONCURRENCY_LIMIT = 10

async def fetch_page(session, url, headers):
    """Fetch a single page asynchronously"""
    try:
        async with session.get(url, headers=headers, timeout=30) as response:
            if response.status != 200:
                print(f"Error: Status {response.status} for {url}")
                return None
            return await response.text()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_jobs_from_html(html, base_url, page_num):
    """Extract job listings from HTML content"""
    if not html:
        return [], None, 0

    soup = BeautifulSoup(html, 'html.parser')
    jobs = []

    # Find all job listings
    job_listings = soup.select('li.lLd3Je')

    for job in job_listings:
        job_data = {'page': page_num}

        # Extract job title
        title_element = job.select_one('h3.QJPWVe')
        job_data['title'] = title_element.text.strip() if title_element else "Unknown"

        # Extract location
        location_element = job.select_one('span.r0wTof')
        job_data['location'] = location_element.text.strip() if location_element else "N/A"

        # Extract experience level
        experience_element = job.select_one('span.wVSTAb')
        job_data['experience_level'] = experience_element.text.strip() if experience_element else "N/A"

        # Extract job URL for details page
        link_element = job.select_one('a.WpHeLc')
        if link_element and link_element.has_attr('href'):
            job_data['url'] = urljoin('https://www.google.com/about/careers/applications', link_element['href'])
        else:
            job_data['url'] = "N/A"

        jobs.append(job_data)

    # Find next page link
    next_button = soup.select_one('div.VfPpkd-Bz112c-LgbsSe[jsname="ViaHrd"] a.WpHeLc')
    next_page_url = None
    if next_button and next_button.has_attr('href'):
        next_page_url = urljoin('https://www.google.com/about/careers/applications', next_button['href'])

    # Get total job count
    total_jobs = 0
    pagination_text = soup.select_one('div.VfPpkd-wZVHld-gruSEe-j4LONd div[jsname="uEp2ad"]')
    if pagination_text:
        match = re.search(r'of\s+(\d+)', pagination_text.text)
        if match:
            total_jobs = int(match.group(1))

    return jobs, next_page_url, total_jobs

def extract_job_details(html):
    """Extract detailed job information from job detail page"""
    if not html:
        return {}

    soup = BeautifulSoup(html, 'html.parser')
    details = {}

    # Extract minimum qualifications
    min_qual_section = soup.find('h3', text='Minimum qualifications:')
    if min_qual_section:
        min_quals = []
        ul = min_qual_section.find_next('ul')
        if ul:
            for li in ul.find_all('li'):
                min_quals.append(li.text.strip())
        details['minimum_qualifications'] = min_quals

    # Extract preferred qualifications
    pref_qual_section = soup.find('h3', text='Preferred qualifications:')
    if pref_qual_section:
        pref_quals = []
        ul = pref_qual_section.find_next('ul')
        if ul:
            for li in ul.find_all('li'):
                pref_quals.append(li.text.strip())
        details['preferred_qualifications'] = pref_quals

    # Extract about the job
    about_section = soup.find('h3', text='About the job')
    if about_section:
        about_text = []
        for p in about_section.find_next_siblings('p'):
            if p.find_next('h3'):  # Stop if we hit the next section
                break
            about_text.append(p.text.strip())
        details['about_job'] = ' '.join(about_text)

    # Extract responsibilities
    resp_section = soup.find('h3', text='Responsibilities')
    if resp_section:
        resp_list = []
        ul = resp_section.find_next('ul')
        if ul:
            for li in ul.find_all('li'):
                resp_list.append(li.text.strip())
        details['responsibilities'] = resp_list

    # Create a full description that combines all sections
    full_description = ""

    if 'minimum_qualifications' in details:
        full_description += "Minimum qualifications:\n"
        for qual in details['minimum_qualifications']:
            full_description += f"{qual}\n"
        full_description += "\n"

    if 'preferred_qualifications' in details:
        full_description += "Preferred qualifications:\n"
        for qual in details['preferred_qualifications']:
            full_description += f"{qual}\n"
        full_description += "\n"

    if 'about_job' in details:
        full_description += "About the job\n"
        full_description += details['about_job'] + "\n\n"

    if 'responsibilities' in details:
        full_description += "Responsibilities\n"
        for resp in details['responsibilities']:
            full_description += f"{resp}\n"

    details['full_description'] = full_description

    return details

async def scrape_google_jobs(base_url):
    """Scrape Google jobs with concurrent requests"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/',
    }

    start_time = time.time()
    all_jobs = []
    total_jobs = 0

    # Create a throttled client session
    conn = aiohttp.TCPConnector(limit=CONCURRENCY_LIMIT)
    async with aiohttp.ClientSession(connector=conn) as session:
        # First, get the total number of jobs and listing pages
        first_page_html = await fetch_page(session, base_url, headers)
        if first_page_html:
            first_page_jobs, next_url, total_jobs = extract_jobs_from_html(first_page_html, base_url, 1)
            all_jobs.extend(first_page_jobs)
            print(f"Found {total_jobs} total jobs. Processing page 1: {len(first_page_jobs)} jobs extracted")

            # Calculate total pages (20 jobs per page)
            estimated_pages = (total_jobs + 19) // 20
            print(f"Estimated {estimated_pages} total pages to process")

            # Create URLs for all pages (2 to estimated_pages)
            urls = [f"{base_url}&page={i}" for i in range(2, estimated_pages + 1)]

            # Process remaining pages in batches
            batch_size = CONCURRENCY_LIMIT
            for i in range(0, len(urls), batch_size):
                batch_urls = urls[i:i+batch_size]

                # Create tasks for batch
                tasks = [fetch_page(session, url, headers) for url in batch_urls]

                # Wait for all tasks to complete
                pages_html = await asyncio.gather(*tasks)

                # Process each page
                for j, html in enumerate(pages_html):
                    page_num = i + j + 2  # +2 because we start from page 2
                    if html:
                        jobs, _, _ = extract_jobs_from_html(html, base_url, page_num)
                        all_jobs.extend(jobs)
                        print(f"Processing page {page_num}: {len(jobs)} jobs extracted")

            # Now fetch job details for each job
            print("\nFetching detailed job descriptions...")

            # Get all job URLs
            job_urls = [job['url'] for job in all_jobs if job['url'] != 'N/A']
            total_details = len(job_urls)

            # Process job details in batches
            for i in range(0, len(job_urls), batch_size):
                batch_urls = job_urls[i:i+batch_size]
                print(f"Fetching details for jobs {i+1}-{min(i+batch_size, total_details)} of {total_details}")

                # Create tasks for batch
                tasks = [fetch_page(session, url, headers) for url in batch_urls]

                # Wait for all tasks to complete
                details_html = await asyncio.gather(*tasks)

                # Process each job detail page
                for j, html in enumerate(details_html):
                    url_index = i + j
                    if url_index < len(all_jobs) and html:
                        # Extract details
                        details = extract_job_details(html)

                        # Find the corresponding job in all_jobs
                        for k, job in enumerate(all_jobs):
                            if job['url'] == job_urls[url_index]:
                                # Update job with details
                                all_jobs[k].update(details)
                                break

                # Add a small delay between batches to be nice to the server
                await asyncio.sleep(1)

    end_time = time.time()
    print(f"Extraction completed in {end_time - start_time:.2f} seconds")
    return all_jobs

def save_to_csv(jobs, filename='google_jobs_with_details.csv'):
    """Save jobs to CSV file with all details"""
    if not jobs:
        print("No jobs to save.")
        return

    # Prepare data for CSV
    csv_data = []
    for job in jobs:
        row = {k: v for k, v in job.items() if not isinstance(v, list) and k != 'full_description'}

        # Handle minimum qualifications
        if 'minimum_qualifications' in job:
            for i, qual in enumerate(job['minimum_qualifications'], 1):
                row[f'min_qual_{i}'] = qual

        # Handle preferred qualifications
        if 'preferred_qualifications' in job:
            for i, qual in enumerate(job['preferred_qualifications'], 1):
                row[f'pref_qual_{i}'] = qual

        # Handle responsibilities
        if 'responsibilities' in job:
            for i, resp in enumerate(job['responsibilities'], 1):
                row[f'responsibility_{i}'] = resp

        # Save description in a separate file
        if 'full_description' in job:
            job_id = job.get('title', '').replace(' ', '_').replace('/', '_')
            job_id = re.sub(r'[^\w\-_]', '', job_id)
            desc_filename = f"descriptions/{job_id}.txt"
            row['description_file'] = desc_filename

            # Make sure directory exists
            os.makedirs('descriptions', exist_ok=True)

            # Save description to file
            with open(desc_filename, 'w', encoding='utf-8') as f:
                f.write(job['full_description'])

        csv_data.append(row)

    # Get all field names
    fieldnames = set()
    for row in csv_data:
        fieldnames.update(row.keys())

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=sorted(fieldnames))
        writer.writeheader()
        writer.writerows(csv_data)

    print(f"Saved {len(jobs)} jobs to {filename}")
    print(f"Job descriptions saved to the 'descriptions' folder")
    return filename

async def main():
    """Main async function"""
    # URL for Google careers with filters
    base_url = "https://www.google.com/about/careers/applications/jobs/results?location=India&target_level=INTERN_AND_APPRENTICE&target_level=EARLY&target_level=MID&employment_type=FULL_TIME"

    print("Starting Google Jobs Scraper with Full Descriptions")
    print("This will first extract all job listings, then visit each job page to get complete descriptions")

    # Extract job listings with details
    all_jobs = await scrape_google_jobs(base_url)

    # Save results
    if all_jobs:
        filename = save_to_csv(all_jobs)
        print(f"Extracted and saved {len(all_jobs)} jobs with full descriptions")

        # Convert to DataFrame for display
        df = pd.DataFrame(all_jobs)

        # Add columns showing which records have various details
        if 'minimum_qualifications' in df.columns:
            df['has_min_quals'] = df['minimum_qualifications'].apply(lambda x: len(x) if isinstance(x, list) else 0)
        if 'preferred_qualifications' in df.columns:
            df['has_pref_quals'] = df['preferred_qualifications'].apply(lambda x: len(x) if isinstance(x, list) else 0)
        if 'responsibilities' in df.columns:
            df['has_resp'] = df['responsibilities'].apply(lambda x: len(x) if isinstance(x, list) else 0)

        # Display summary
        print("\nSummary Statistics:")
        print(f"Total jobs found: {len(df)}")
        print(f"Unique job titles: {df['title'].nunique()}")

        # Show stats on detail extraction success
        with_desc = df['full_description'].notna().sum() if 'full_description' in df.columns else 0
        print(f"Jobs with full descriptions: {with_desc} ({with_desc/len(df)*100:.1f}%)")

        return df
    else:
        print("No jobs were extracted")
        return pd.DataFrame()

if __name__ == "__main__":
    df_jobs = asyncio.run(main())
