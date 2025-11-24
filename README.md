# Company Research Assistant - Account Plan Generator

An AI-powered tool that helps research companies and generate comprehensive account plans using Gemini API.

## 📁 Project Structure

```
project/
├── app.py              # Streamlit frontend application
├── generator.py        # AI model & API logic
├── utils.py           # Helper functions & file operations
├── requirements.txt   # Python dependencies
├── .env              # Environment variables (create this)
└── data/             # Auto-created for storage
    ├── conversation_history.json
    ├── account_plan.json
    ├── output.json
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 How to Use

### Step 1: Research a Company
In the Chat tab, type:
- "Research Tesla"
- "Tell me about Microsoft"
- "Find information on Apple Inc"

The AI will search the web and compile comprehensive research.

### Step 2: Generate Account Plan
After research is complete, type:
- "Generate account plan"
- "Create plan"
- "Yes"

The AI will create a structured account plan with 7 sections.

### Step 3: Edit Sections
Go to the "Account Plan" tab and:
- Click the ✏️ Edit button on any section
- Modify the content
- Click 💾 Save to update

### Step 4: Export
Click "📥 Export Plan" in the sidebar to download as JSON.

## 🎯 Features

### Research Capabilities
- ✅ Web search integration via Gemini API
- ✅ Multi-source information gathering
- ✅ Real-time company data
- ✅ News, financials, competitors, leadership

### Account Plan Generation
- ✅ Company Overview
- ✅ Key Stakeholders
- ✅ Pain Points Analysis
- ✅ Value Proposition
- ✅ Engagement Strategy
- ✅ Success Metrics

### Data Management
- ✅ Persistent storage (JSON files)
- ✅ Conversation history
- ✅ Automatic backups
- ✅ Export to JSON
- ✅ Section-level editing

## 📂 File Descriptions

### `app.py`
Main Streamlit application with:
- Chat interface
- Account plan display
- Section editing UI
- Export functionality

### `generator.py`
AI logic including:
- `ResearchGenerator`: Main class for AI interactions
- `research_company()`: Web search & research
- `generate_account_plan()`: Plan creation
- `regenerate_section()`: Update specific sections
- `chat()`: General conversation

### `utils.py`
Helper functions:
- `save_account_plan()`: Store plans to JSON
- `load_account_plan()`: Retrieve stored plans
- `save_conversation_history()`: Save chat logs
- `export_plan_to_json()`: Export formatted JSON
- `validate_account_plan()`: Check plan completeness
- File backup and cleanup utilities

### `data/output.json`
Stores the final exported account plans with metadata:
```json
{
  "data": { ... },
  "timestamp": "2024-11-24T10:30:00",
  "type": "account_plan_output"
}
```

## 💡 Usage Examples

### Example 1: Basic Research
```
User: Research Salesforce
Assistant: [Performs web search]
         [Returns comprehensive research]
User: Generate account plan
Assistant: [Creates structured plan]
```

### Example 2: Editing Sections
1. Go to "Account Plan" tab
2. Click "✏️ Edit" on "Pain Points"
3. Modify text
4. Click "💾 Save"

### Example 3: Export
1. Click "📥 Export Plan" in sidebar
2. Choose "Download JSON"
3. File saved as `account_plan_YYYYMMDD_HHMMSS.json`

## 🐛 Troubleshooting

**"API Key Error"**
- Ensure your `.env` file contains valid API key
- Or enter key directly in the Streamlit sidebar

**"No research data found"**
- Make sure to research a company first before generating plan
- Check internet connection for web search

**"Plan generation failed"**
- Check API key is valid
- Ensure research data was successfully retrieved
- Try researching the company again

**"File not found errors"**
- The `data/` directory is created automatically
- Check file permissions in your project folder

## 📊 Data Files

### `conversation_history.json`
```json
[
  {
    "role": "user",
    "content": "Research Tesla",
    "timestamp": "2024-11-24T10:00:00"
  },
  {
    "role": "assistant",
    "content": "Research findings...",
    "type": "research",
    "timestamp": "2024-11-24T10:00:30"
  }
]
```

### `account_plan.json`
```json
{
  "plan": {
    "company_overview": "...",
    "key_stakeholders": "...",
    "pain_points": "...",
    "value_proposition": "...",
    "engagement_strategy": "...",
    "success_metrics": "...",
    "next_steps": "..."
  },
  "created_at": "2024-11-24T10:05:00",
  "version": "1.0"
}
```

## 🎓 Assignment Notes

This implementation fulfills all requirements:
- ✅ Interactive agent with natural conversation
- ✅ Multi-source information gathering (web search)
- ✅ Real-time research updates and confirmations
- ✅ Account plan generation
- ✅ Section-level editing and regeneration
- ✅ Persistent storage (JSON files)
- ✅ Clean separation of concerns (app/generator/utils)

Perfect for your Company Research Assistant assignment! 🚀