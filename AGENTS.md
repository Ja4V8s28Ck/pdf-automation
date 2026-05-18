# AI Workflow Document

## AI Tools Used
- **Claude Code (opencode)** — Primary development assistant for code generation, architecture decisions, and implementation
- **Google Gemini API** — Used for vision-based data extraction from handwritten manufacturing documents

## How AI Tools Were Used

### Claude Code (opencode)
- **Architecture planning**: Used to evaluate tech stack options and design the application structure
- **Code generation**: Generated all Python modules, Streamlit pages, and configuration files
- **Database design**: Created SQLAlchemy models and database operations
- **Validation logic**: Implemented business rules for data validation
- **UI/UX**: Built Streamlit multi-page application with consistent navigation

### Google Gemini API
- **Document understanding**: Used Gemini 2.0 Flash's vision capabilities to extract structured data from handwritten manufacturing forms
- **Confidence scoring**: Prompted to return per-field confidence scores alongside extracted values
- **Structured output**: Configured to return JSON formatted extraction results

## Prompting/Debugging Workflows
- **Extraction prompt**: Iteratively refined to specify exact JSON output format, confidence scoring criteria, and handling of empty/illegible fields
- **Validation rules**: Defined declaratively with clear separation from extraction logic
- **Error handling**: Added try/catch around API calls with user-facing error messages

## Areas Where AI Helped Most
1. Rapid prototyping — complete multi-page app generated in minutes
2. Database schema design — consistent ORM models with relationships
3. Streamlit UI patterns — consistent layout and navigation across pages
4. Validation logic — comprehensive rule coverage with clear separation of concerns

## Areas Requiring Manual Intervention
1. **Gemini API key setup** — User must obtain their own API key
2. **Prompt tuning** — Extraction quality depends on prompt refinement for the specific document format
3. **Edge case handling** — Some document formats may need custom extraction prompts
4. **UI fine-tuning** — Streamlit layout adjustments for specific use cases
