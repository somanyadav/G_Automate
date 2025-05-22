# 🎯 AI-Powered Job Analysis & Notification System

> **Automated weekly job scraping, AI-powered resume matching, and intelligent job recommendations delivered straight to your inbox**

[![GitHub Actions](https://img.shields.io/badge/GitHub-Actions-blue?logo=github-actions)](https://github.com/features/actions)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![Google AI](https://img.shields.io/badge/Google-Generative%20AI-orange?logo=google)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 🌟 What This System Does

This automated system revolutionizes your job search by:

- **🔍 Scrapes Google Careers** for jobs matching your criteria
- **🤖 Uses Google's Gemini AI** to analyze job-resume fit
- **📊 Scores each job** (0-10) based on your qualifications  
- **📧 Sends weekly notifications** with your best matches
- **⚡ Runs completely automatically** every Sunday
- **💰 Saves time and money** through intelligent filtering
- **📈 Tracks your progress** over time

### Key Features

- **Intelligent Pre-filtering**: Uses AI embeddings to filter relevant jobs before expensive analysis
- **Comprehensive Analysis**: Extracts minimum qualifications, preferred skills, and responsibilities
- **Smart Scoring**: Rates job fit from 0-10 with detailed reasoning
- **Personalized Outreach**: Generates LinkedIn networking messages for each role
- **Mobile-Friendly**: Beautiful email format that works on all devices
- **Cost-Effective**: Built-in caching prevents redundant API calls
- **Zero Maintenance**: Fully automated with error handling

## 🚀 Quick Start

### Prerequisites

- GitHub account
- Google Cloud account with Generative AI API access
- Your resume in PDF format

### 5-Minute Setup

1. **Fork this repository** or create a new one
2. **Upload your files** (see [File Structure](#file-structure))
3. **Configure secrets** (see [Environment Setup](#environment-setup))
4. **Test the workflow** manually
5. **Enjoy weekly job notifications!**

## 📁 File Structure

```
your-repository/
├── .github/
│   └── workflows/
│       └── job-analysis-workflow.yml     # GitHub Actions workflow
├── job_scraper.py                        # Web scraper for Google Careers
├── job_analyzer.py                       # AI-powered job analysis
├── send_job_email_simple.py              # Email notification system
├── requirements.txt                      # Python dependencies
├── resume.pdf                            # Your resume (REQUIRED)
├── README.md                             # This file
└── .gitignore                           # Git ignore patterns
```

### Generated Files (Auto-created)

```
├── google_jobs_with_details.csv          # All scraped jobs
├── analyzed_google_jobs_full.csv         # All jobs with AI analysis
├── shortlisted_google_jobs_full.csv      # Top matching jobs only
├── job_notification_email.txt            # Email content for manual sending
├── llm_response_cache.json               # AI response cache
└── descriptions/                         # Individual job description files
    ├── Software_Engineer_ML.txt
    ├── Product_Manager.txt
    └── ...
```

## ⚙️ Environment Setup

### 1. Google AI API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key value

### 2. GitHub Secrets Configuration

Go to your repository: **Settings → Secrets and variables → Actions**

Add these secrets:

| Secret Name | Description | Required | Example |
|-------------|-------------|----------|---------|
| `GOOGLE_API_KEY` | Google Generative AI API key | ✅ Yes | `AIzaSyB...` |
| `SENDER_EMAIL` | Gmail address for sending notifications | ⚠️ Optional* | `your.email@gmail.com` |
| `SENDER_APP_PASSWORD` | Gmail App Password | ⚠️ Optional* | `abcd efgh ijkl mnop` |
| `RECIPIENT_EMAIL` | Where to receive notifications | ⚠️ Optional* | `notifications@gmail.com` |

*Email secrets are optional if using the simple file-based notification system

### 3. Gmail App Password Setup (Optional)

If you want email notifications:

1. Enable [2-Step Verification](https://myaccount.google.com/security) on your Google account
2. Go to [App Passwords](https://myaccount.google.com/apppasswords)
3. Generate a new app password for "Mail"
4. Use this 16-character password in `SENDER_APP_PASSWORD`

## 🛠️ Installation & Configuration

### Step 1: Repository Setup

1. **Create/Fork Repository**
   ```bash
   git clone https://github.com/yourusername/job-analysis-system.git
   cd job-analysis-system
   ```

2. **Add Your Resume**
   - Name your resume file exactly: `resume.pdf`
   - Place it in the repository root
   - Ensure it's a readable PDF with extractable text

3. **Upload All Files**
   - Copy all Python files from this guide
   - Create the `.github/workflows/` directory structure
   - Add the workflow YAML file

### Step 2: Customize Job Search Filters

Edit `job_scraper.py` to modify search criteria:

```python
# Current settings: India, Intern/Early/Mid level, Full-time
base_url = "https://www.google.com/about/careers/applications/jobs/results?location=India&target_level=INTERN_AND_APPRENTICE&target_level=EARLY&target_level=MID&employment_type=FULL_TIME"

# Example customizations:

# United States, Senior level
base_url = "https://www.google.com/about/careers/applications/jobs/results?location=United%20States&target_level=SENIOR&employment_type=FULL_TIME"

# Remote jobs, All levels
base_url = "https://www.google.com/about/careers/applications/jobs/results?location=Remote&employment_type=FULL_TIME"

# Specific location: San Francisco
base_url = "https://www.google.com/about/careers/applications/jobs/results?location=San%20Francisco%2C%20CA%2C%20USA&employment_type=FULL_TIME"
```

### Step 3: Configure Analysis Parameters

Edit `job_analyzer.py` to adjust AI analysis settings:

```python
# Embedding similarity threshold (0.0-1.0, higher = more strict)
EMBEDDING_SIMILARITY_THRESHOLD = 0.55  # Recommended: 0.5-0.7

# Maximum jobs to analyze after embedding filter
MAX_JOBS_AFTER_EMBEDDING_FILTER = 200  # Recommended: 100-300

# Minimum fit score for shortlisting (0-10)
desired_fit_score_threshold = 7  # Recommended: 6-8

# Categories to include in shortlist
desired_categories = ["Strong Fit", "Potential Fit"]
```

### Step 4: Schedule Configuration

Edit `.github/workflows/job-analysis-workflow.yml` to change the schedule:

```yaml
on:
  schedule:
    # Every Sunday at 9:00 AM UTC
    - cron: '0 9 * * 0'
    
    # Other examples:
    # Every day at 6:00 AM UTC
    # - cron: '0 6 * * *'
    
    # Every Monday and Friday at 8:00 AM UTC
    # - cron: '0 8 * * 1,5'
    
    # Twice a week: Wednesday and Sunday
    # - cron: '0 9 * * 3,0'
```

## 🎮 Usage Guide

### Manual Testing

1. **Go to Actions tab** in your GitHub repository
2. **Click "Weekly Job Analysis"** workflow
3. **Click "Run workflow"** to test manually
4. **Monitor the progress** in real-time

### Automatic Operation

- **Runs every Sunday** at 9:00 AM UTC (configurable)
- **No intervention required** - fully automated
- **Handles errors gracefully** with detailed logging
- **Caches results** to minimize costs

### Accessing Results

#### Option 1: Artifacts (Temporary - 30 days)
1. Go to **Actions → Recent workflow run**
2. Scroll to **"Artifacts"** section
3. Download **"job-analysis-results.zip"**
4. Extract and review files

#### Option 2: Repository Files (Permanent)
- Results are **automatically committed** to your repo
- Browse CSV files directly on GitHub
- **Version history** shows changes over time
- Files persist indefinitely

#### Option 3: Email Notifications (If configured)
- **Weekly email** with top job matches
- **Beautiful HTML format** with direct apply links
- **Attachment** with complete job details
- **Mobile-optimized** for on-the-go reading

## 📊 Understanding the Results

### File Descriptions

#### `google_jobs_with_details.csv`
**All scraped jobs with complete information**

| Column | Description | Example |
|--------|-------------|---------|
| `title` | Job title | "Software Engineer, Machine Learning" |
| `location` | Job location | "Mountain View, CA, USA" |
| `experience_level` | Required experience | "Mid" |
| `url` | Direct application link | "https://careers.google.com/jobs/..." |
| `min_qual_1`, `min_qual_2`, ... | Minimum qualifications | "Bachelor's degree in Computer Science" |
| `pref_qual_1`, `pref_qual_2`, ... | Preferred qualifications | "Experience with TensorFlow" |
| `responsibility_1`, `responsibility_2`, ... | Job responsibilities | "Design and implement ML models" |

#### `analyzed_google_jobs_full.csv`
**All jobs with AI analysis (includes errors)**

Additional columns:
| Column | Description | Example |
|--------|-------------|---------|
| `fit_score` | AI-generated fit score (0-10) | 8 |
| `fit_category` | Fit category | "Strong Fit" |
| `key_matches` | Skills that match your resume | "['Python', 'Machine Learning', 'TensorFlow']" |
| `potential_gaps` | Skills you might need to develop | "['Distributed Systems', 'Kubernetes']" |
| `reasoning_summary` | AI explanation of the score | "Strong match due to ML experience..." |
| `auto_drafted_outreach_snippet` | LinkedIn message template | "I noticed your ML role..." |

#### `shortlisted_google_jobs_full.csv`
**Only the best matching jobs (score ≥7)**

- Same structure as analyzed file
- **Filtered for quality** - only high-scoring jobs
- **Sorted by fit score** (best matches first)
- **Ready for action** - these are your target applications

### Interpreting Scores

| Score Range | Category | Meaning | Action |
|-------------|----------|---------|--------|
| **9-10** | Excellent Match | Perfect fit, apply immediately | **High Priority** - Apply ASAP |
| **8-8.9** | Strong Fit | Very good match, strong candidate | **Priority** - Apply this week |
| **7-7.9** | Good Fit | Solid match, worth applying | **Consider** - Apply if interested |
| **6-6.9** | Potential Fit | Some gaps, but viable | **Maybe** - Apply with skill development plan |
| **5-5.9** | Borderline | Significant gaps | **Skip** - Focus on skill building |
| **0-4.9** | Poor Fit | Not a good match | **Skip** - Look for better matches |

### Sample Job Analysis Output

```
Job Title: Senior Software Engineer, AI/ML Platform
Location: San Francisco, CA
Fit Score: 8.5/10
Fit Category: Strong Fit

Key Matches:
• Python programming (5+ years)
• Machine Learning model development
• TensorFlow/PyTorch experience
• Data pipeline architecture
• Cloud platforms (GCP/AWS)

Potential Gaps:
• Kubernetes orchestration
• Large-scale distributed systems
• MLOps pipeline experience

Reasoning: Strong technical alignment with ML background and Python expertise. 
Minor gaps in infrastructure areas can be learned on the job.

Outreach Snippet: "I was excited to see your AI/ML Platform role, especially the 
focus on TensorFlow and data pipelines which align perfectly with my recent projects 
at [Previous Company]. I'd love to learn more about your team's approach to 
scalable ML infrastructure."
```

## 🎨 Customization Options

### Job Search Filters

Modify the Google Careers URL in `job_scraper.py`:

**Location Examples:**
```python
# United States
"location=United%20States"

# Remote only
"location=Remote"

# Specific city
"location=New%20York%2C%20NY%2C%20USA"

# Multiple locations (not directly supported, use separate runs)
```

**Experience Level Examples:**
```python
# Entry level only
"target_level=INTERN_AND_APPRENTICE&target_level=EARLY"

# Senior level only  
"target_level=SENIOR"

# All levels
"target_level=INTERN_AND_APPRENTICE&target_level=EARLY&target_level=MID&target_level=SENIOR"
```

**Employment Type Examples:**
```python
# Full-time only
"employment_type=FULL_TIME"

# Include part-time and contract
"employment_type=FULL_TIME&employment_type=PART_TIME&employment_type=CONTRACT"
```

### AI Analysis Tuning

**For More Selective Results (Higher Quality, Fewer Jobs):**
```python
EMBEDDING_SIMILARITY_THRESHOLD = 0.7  # Higher threshold
MAX_JOBS_AFTER_EMBEDDING_FILTER = 50  # Fewer jobs to analyze
desired_fit_score_threshold = 8  # Higher score requirement
```

**For More Comprehensive Results (Lower Quality, More Jobs):**
```python
EMBEDDING_SIMILARITY_THRESHOLD = 0.4  # Lower threshold
MAX_JOBS_AFTER_EMBEDDING_FILTER = 500  # More jobs to analyze
desired_fit_score_threshold = 6  # Lower score requirement
```

**Cost vs. Quality Trade-offs:**
- **Higher thresholds** = Better matches, lower API costs
- **Lower thresholds** = More opportunities, higher API costs
- **Sweet spot**: 0.55 threshold, 200 jobs, score ≥7

### Email Customization

Edit `send_job_email_simple.py` to modify email content:

```python
# Change subject line format
subject = f"🎯 {len(df_shortlisted)} Jobs for You - {datetime.now().strftime('%b %d')}"

# Modify email sections
email_body += """
🔥 URGENT APPLICATIONS (Score 9+):
{urgent_jobs}

⭐ HIGH PRIORITY (Score 8+):
{high_priority_jobs}

💡 WORTH CONSIDERING (Score 7+):
{worth_considering_jobs}
"""

# Add custom sections
email_body += """
📚 SKILL DEVELOPMENT RECOMMENDATIONS:
Based on this week's job analysis, consider learning:
• {top_missing_skill_1}
• {top_missing_skill_2}
• {top_missing_skill_3}
"""
```

## 🔧 Advanced Configuration

### Multi-Company Support

To scrape jobs from multiple companies, create separate workflow files:

```yaml
# .github/workflows/google-jobs.yml
name: Google Jobs Analysis

# .github/workflows/microsoft-jobs.yml  
name: Microsoft Jobs Analysis

# .github/workflows/amazon-jobs.yml
name: Amazon Jobs Analysis
```

Each with different base URLs and schedules.

### Custom Resume Processing

For multiple resumes or resume versions:

```python
# In job_analyzer.py
PDF_RESUME_FILES = {
    "technical": "resume_technical.pdf",
    "product": "resume_product.pdf", 
    "general": "resume_general.pdf"
}

# Process each resume type
for resume_type, resume_file in PDF_RESUME_FILES.items():
    # Run analysis with specific resume
    # Save results with resume_type prefix
```

### Industry-Specific Analysis

Add industry-specific scoring logic:

```python
def calculate_industry_bonus(job_title, job_description, target_industry):
    """Add bonus points for target industry jobs"""
    industry_keywords = {
        "fintech": ["banking", "financial", "payments", "trading"],
        "healthcare": ["medical", "hospital", "health", "clinical"],
        "edtech": ["education", "learning", "teaching", "academic"]
    }
    
    bonus = 0
    for keyword in industry_keywords.get(target_industry, []):
        if keyword.lower() in job_title.lower() or keyword.lower() in job_description.lower():
            bonus += 0.5
    
    return min(bonus, 2.0)  # Max 2 point bonus
```

### Performance Optimization

**For Large-Scale Operations:**

```python
# Increase concurrency for faster scraping
CONCURRENCY_LIMIT = 20  # Default: 10

# Batch processing for API calls
EMBEDDING_BATCH_SIZE = 50  # Process embeddings in batches
LLM_BATCH_SIZE = 10       # Process LLM calls in batches

# Implement rate limiting
import time
time.sleep(0.1)  # 100ms delay between requests
```

**For Cost Optimization:**

```python
# Aggressive pre-filtering
USE_EMBEDDING_PRE_FILTERING = True
EMBEDDING_SIMILARITY_THRESHOLD = 0.65  # Higher threshold

# Cache everything
CACHE_EMBEDDINGS = True
CACHE_LLM_RESPONSES = True
CACHE_EXPIRY_DAYS = 30

# Limit analysis scope
MAX_JOBS_TO_ANALYZE_WITH_LLM = 100
```

## 🚨 Troubleshooting

### Common Issues & Solutions

#### ❌ "resume.pdf not found"
**Cause**: Resume file missing or incorrectly named
**Solution**: 
- Ensure file is named exactly `resume.pdf` (case-sensitive)
- Place in repository root directory
- Verify file is uploaded to GitHub

#### ❌ "GOOGLE_API_KEY not found"
**Cause**: API key not properly configured
**Solution**:
- Check GitHub repository Settings → Secrets → Actions
- Verify secret name is exactly `GOOGLE_API_KEY`
- Test API key at [Google AI Studio](https://makersuite.google.com/)

#### ❌ "No jobs found" or "Empty results"
**Cause**: Search filters too restrictive or Google page structure changed
**Solutions**:
- Test your search URL manually in browser
- Broaden location/level filters
- Check if Google Careers site is accessible
- Verify job listing CSS selectors haven't changed

#### ❌ "API quota exceeded" or "Rate limit hit"
**Cause**: Too many API calls in short period
**Solutions**:
- Increase `EMBEDDING_SIMILARITY_THRESHOLD` to filter more jobs
- Reduce `MAX_JOBS_AFTER_EMBEDDING_FILTER`
- Add delays between API calls
- Monitor usage at [Google Cloud Console](https://console.cloud.google.com/)

#### ❌ "Workflow failed" or "Python errors"
**Cause**: Code issues or missing dependencies
**Solutions**:
- Check Actions logs for specific error messages
- Verify all files are uploaded correctly
- Ensure `requirements.txt` includes all dependencies
- Test code locally before committing

#### ❌ "Email sending failed"
**Cause**: Gmail authentication issues
**Solutions**:
- Use the simple file-based email system
- Verify 2-Factor Authentication is enabled
- Generate new Gmail App Password
- Try alternative email providers

### Debugging Tips

#### Enable Verbose Logging
Add debug prints to track progress:

```python
# In job_analyzer.py
print(f"DEBUG: Processing job {job_title}")
print(f"DEBUG: Embedding similarity: {similarity_score}")
print(f"DEBUG: LLM response: {assessment_json}")
```

#### Test Components Individually

**Test Job Scraper Only:**
```bash
python job_scraper.py
```

**Test Job Analyzer Only:**
```bash
# Ensure google_jobs_with_details.csv exists first
python job_analyzer.py
```

**Test Email System Only:**
```bash
# Ensure shortlisted_google_jobs_full.csv exists first
python send_job_email_simple.py
```

#### Monitor API Usage

Check your Google Cloud Console for:
- API request counts
- Error rates
- Quota remaining
- Cost tracking

#### Check File Permissions

Ensure GitHub Actions can write files:
```yaml
permissions:
  contents: write  # Allow writing files to repository
  actions: read    # Allow reading workflow files
```

### Performance Issues

#### Slow Execution
- **Reduce concurrency**: Lower `CONCURRENCY_LIMIT`
- **Add delays**: Increase `time.sleep()` values
- **Process fewer jobs**: Lower `MAX_JOBS_AFTER_EMBEDDING_FILTER`

#### High Costs
- **Increase filtering**: Higher `EMBEDDING_SIMILARITY_THRESHOLD`
- **Cache aggressively**: Enable all caching options
- **Limit scope**: Process fewer job pages

#### Memory Issues
- **Process in batches**: Split large job lists
- **Clear variables**: Delete large objects when done
- **Optimize pandas**: Use `dtype` specifications

## 💰 Cost Analysis

### Google Generative AI API Pricing

**Text Embedding (text-embedding-004):**
- **Free tier**: 1,500 requests/day
- **Paid**: $0.00025 per 1K characters

**Gemini 1.5 Flash:**
- **Free tier**: 15 requests/minute, 1,500 requests/day
- **Paid**: $0.075 per 1M input tokens, $0.30 per 1M output tokens

### Cost Estimation

**Weekly Analysis for 100 Jobs:**

| Component | Usage | Cost (Approx) |
|-----------|-------|---------------|
| Job Embeddings | 100 × 500 chars = 50K chars | $0.01 |
| Resume Embedding | 1 × 5K chars = 5K chars | $0.001 |
| LLM Analysis | 50 jobs × 3K tokens = 150K tokens | $0.01 |
| **Total per week** | | **~$0.02** |
| **Total per month** | | **~$0.08** |
| **Total per year** | | **~$1.00** |

### Cost Optimization Strategies

1. **Use Free Tier**: Stay within daily limits (1,500 requests/day)
2. **Aggressive Filtering**: Higher similarity thresholds
3. **Smart Caching**: Cache embeddings and LLM responses
4. **Batch Processing**: Reduce API overhead
5. **Targeted Searches**: Use specific job filters

**Example Low-Cost Configuration:**
```python
EMBEDDING_SIMILARITY_THRESHOLD = 0.7  # Filter out 70%+ of jobs
MAX_JOBS_AFTER_EMBEDDING_FILTER = 50  # Analyze only top 50
desired_fit_score_threshold = 8       # Only high-quality matches
```

## 🔒 Security & Privacy

### Data Handling

**Your Resume:**
- ✅ Stays in your private GitHub repository
- ✅ Never sent to external services except Google AI API
- ✅ Processed only for job matching
- ✅ Can be removed anytime

**Job Data:**
- ✅ Public information from Google Careers
- ✅ Cached locally in your repository
- ✅ No personal information stored

**API Keys:**
- ✅ Stored securely in GitHub Secrets
- ✅ Never exposed in logs or files
- ✅ Encrypted at rest and in transit

### Best Practices

1. **Use GitHub Secrets** for all sensitive data
2. **Never commit API keys** to repository
3. **Regular key rotation** (quarterly recommended)
4. **Monitor API usage** for unusual activity
5. **Keep repository private** if containing sensitive info

### Compliance Considerations

- **Resume data**: Ensure compliance with local privacy laws
- **Job scraping**: Respects robots.txt and rate limits
- **API usage**: Follows Google's terms of service
- **Data retention**: Configurable retention periods

## 📈 Monitoring & Maintenance

### Success Metrics

Track these KPIs over time:

| Metric | What it Measures | Target |
|--------|------------------|---------|
| **Jobs Scraped** | System reach | 500+ per week |
| **Jobs Shortlisted** | Filtering effectiveness | 10-50 per week |
| **Average Fit Score** | Match quality | 7.5+ average |
| **Application Rate** | User action | 5-10% of shortlisted |
| **Interview Rate** | System effectiveness | 10-20% of applications |

### Health Checks

**Weekly Monitoring:**
- ✅ Workflow execution success
- ✅ Number of jobs found
- ✅ API quota usage
- ✅ Error rates in logs

**Monthly Reviews:**
- 📊 Update job search filters
- 📊 Adjust AI parameters
- 📊 Review cost trends
- 📊 Update resume if needed

### Maintenance Tasks

**Quarterly:**
- 🔄 Rotate API keys
- 🔄 Update dependencies
- 🔄 Review and optimize parameters
- 🔄 Clean up old cache files

**Annually:**
- 📝 Update resume
- 📝 Review search criteria
- 📝 Evaluate alternative platforms
- 📝 Assess ROI and effectiveness

### Alerts & Notifications

Set up monitoring for:

**Critical Issues:**
- Workflow failures
- API authentication errors
- Zero jobs found (indicates issues)

**Warning Conditions:**
- High API costs
- Low job match rates
- Slow execution times

## 🎯 Success Stories & Use Cases

### Typical User Journey

**Week 1:** Setup and Configuration
- User sets up the system following this guide
- First run finds 45 jobs, 8 shortlisted
- User applies to top 3 matches

**Week 2-4:** Fine-tuning
- Adjusts similarity threshold based on results
- Updates resume based on gap analysis
- Refines job search criteria

**Month 2:** Optimization
- System consistently finds 10-15 quality matches
- User applies to 2-3 jobs per week
- Starts getting interview requests

**Month 3:** Success
- User lands interviews from system recommendations
- Receives job offers
- Continues using system for market intelligence

### Real-World Examples

**Software Engineer (3 years experience):**
- **Search**: "Software Engineer" + "Machine Learning" in Bay Area
- **Results**: 15-20 matches weekly, 8.5 average score
- **Outcome**: 3 interviews in 6 weeks, 2 offers

**Product Manager (5 years experience):**
- **Search**: "Product Manager" + Remote + Tech companies
- **Results**: 8-12 matches weekly, 7.8 average score
- **Outcome**: Networking via outreach snippets led to referrals

**Recent Graduate:**
- **Search**: "Entry Level" + "Software Engineer" + Major cities
- **Results**: 25-30 matches weekly, 7.2 average score
- **Outcome**: Skill gap analysis guided learning priorities

### Industry Adaptations

**Finance/Banking:**
```python
# Focus on fintech and banking roles
base_url_additions = "&q=finance+OR+banking+OR+fintech"
industry_keywords = ["financial", "trading", "payments", "banking"]
```

**Healthcare:**
```python
# Healthcare and biotech focus
base_url_additions = "&q=healthcare+OR+medical+OR+biotech"
industry_keywords = ["health", "medical", "clinical", "pharmaceutical"]
```

**Startups:**
```python
# Startup and growth company focus
base_url_additions = "&q=startup+OR+series+OR+growth"
company_size_preference = "small_to_medium"
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Generative AI** for powerful language models
- **GitHub Actions** for free automation platform
- **Beautiful Soup** for web scraping capabilities
- **Pandas** for data manipulation
- **The open-source community** for inspiration and tools

## 📞 Support

Need help? Here are your options:

1. **📖 Check this README** - Most questions are answered here
2. **🔍 Search existing issues** - Someone may have had the same problem
3. **💬 Open a discussion** - For general questions and ideas
4. **🐛 Create an issue** - For bugs and feature requests
5. **📧 Email support** - For private/sensitive questions

---

## ⭐ Star This Project

If this system helps you land your dream job, please give it a star! ⭐

**Happy Job Hunting!** 🎯🚀

---

*Last updated: May 22, 2025*
*Version: 1.0.0*
