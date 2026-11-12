# Resume Evaluator AI: Intelligent Resume Screening Platform

Resume Evaluator AI is a full-stack web application that leverages large language models running on NIMs to provide intelligent resume evaluation and candidate assessment. The platform helps hiring managers and recruiters make data-driven decisions by automatically scoring resumes against job descriptions and providing actionable improvement suggestions.

## 🌟 Features

- **Automated Resume Scoring**: AI-powered evaluation of resumes on a 1-10 scale based on job requirements
- **Candidate Name Extraction**: Automatic identification of candidate names from resume text
- **Detailed Justifications**: Clear explanations for each score with specific strengths and gaps
- **Improvement Suggestions**: Personalized recommendations for candidates to enhance their profiles
- **Batch Processing**: Evaluate multiple resumes simultaneously against a single job description
- **Visual Analytics**: Scatter plot visualization of candidate scores for easy comparison
- **PDF Resume Support**: Extract text from PDF resumes for evaluation
- **Real-time Processing**: Streaming responses from NVIDIA's Llama 3.1 405B model

## 🏗️ Architecture

### Technical Stack

- **Frontend**: React 18 with TypeScript and Material-UI
- **Backend**: Node.js with Express.js
- **AI Model**: NVIDIA Llama 3.1 405B Instruct via API
- **Visualization**: Chart.js and Recharts for data visualization
- **PDF Processing**: pdf-lib and react-pdftotext for resume parsing

### System Architecture

```
┌─────────────────────┐         ┌─────────────────────┐         ┌─────────────────────┐
│                     │         │                     │         │                     │
│   React Frontend    │ <-----> │   Express Backend   │ <-----> │   NVIDIA NIMs API   │
│   (Port 3000)       │  HTTP   │   (Port 3001)       │  HTTPS  │   (Llama 3.1 405B)  │
│                     │         │                     │         │                     │
└─────────────────────┘         └─────────────────────┘         └─────────────────────┘
```

### Key Components

| Component | Purpose |
|-----------|---------|
| **InputSection** | Handles job description input and resume uploads |
| **OutputSection** | Displays evaluation results and visualizations |
| **LLM Controller** | Manages AI model interactions and prompt engineering |
| **Scatterplot** | Visualizes candidate scores for comparison |

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ and npm
- NVIDIA API key (get from [NVIDIA NGC](https://build.nvidia.com))
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Installation

1. **Clone and navigate to the project**:
```bash
cd projects/resume-evaluator-ai
```

2. **Backend Setup**:
```bash
cd backend/express-llm
npm install

# Create .env file
echo "NVIDIA_API_KEY=your_nvidia_api_key_here" > .env
```

3. **Frontend Setup** (in a new terminal):
```bash
cd frontend
npm install
```

4. **Start the Application**:

Backend (Terminal 1):
```bash
cd backend/express-llm
node app.js
# Server runs on http://localhost:3001
```

Frontend (Terminal 2):
```bash
cd frontend
npm start
# App opens at http://localhost:3000
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in `backend/express-llm/`:

```env
NVIDIA_API_KEY=your_nvidia_api_key_here
```

### API Configuration

The backend is configured to use:
- **Model**: `meta/llama-3.1-405b-instruct`
- **Temperature**: 0.2 (for consistent results)
- **Top-p**: 0.7
- **Max Tokens**: 1024
- **Streaming**: Enabled for real-time responses

## 📋 Usage Guide

### 1. Input Job Information
- Enter company name and role title
- Provide detailed job description

### 2. Upload Resumes
- Upload multiple PDF resumes or paste text directly
- System extracts and processes resume content

### 3. Generate Evaluations
- Click "Generate Score" to evaluate all resumes
- AI analyzes each resume against the job description

### 4. Review Results
- View scores (1-10) for each candidate
- Read detailed justifications for each score
- Check resume summaries and key qualifications
- Get improvement suggestions for candidates

### 5. Visualize Data
- Use scatter plot to compare candidates visually
- Identify top performers at a glance

## 🎯 Use Cases

### Recruitment & HR
- **High-Volume Screening**: Process hundreds of resumes quickly
- **Consistent Evaluation**: Remove bias with standardized AI scoring
- **Candidate Feedback**: Provide constructive suggestions to applicants

### Staffing Agencies
- **Client Matching**: Match candidates to multiple job openings
- **Quality Assurance**: Ensure submitted candidates meet requirements
- **Reporting**: Generate evaluation reports for clients

### Career Services
- **Resume Optimization**: Help job seekers improve their resumes
- **Skills Gap Analysis**: Identify areas for professional development
- **Mock Evaluations**: Practice before real applications

### Educational Institutions
- **Career Counseling**: Guide students in resume writing
- **Industry Alignment**: Ensure curricula match job market needs
- **Placement Support**: Improve student job placement rates

## 📚 Educational Playbook

The `playbook/` directory contains a Jupyter notebook (`ResumeEvaluator.ipynb`) that demonstrates:

### Learning Objectives
1. **Prompt Engineering**: Crafting effective prompts for resume evaluation
2. **LLM Integration**: Working with NVIDIA's API endpoints
3. **Response Parsing**: Extracting structured data from LLM outputs
4. **Full-Stack Development**: Building AI-powered web applications

### Running the Playbook
```bash
cd playbook
jupyter notebook ResumeEvaluator.ipynb
```

## 💡 Key Features Explained

### Intelligent Scoring Algorithm
- Uses few-shot learning with example evaluations
- Considers multiple factors: skills, experience, education, achievements
- Provides nuanced scores (not just keyword matching)

### Contextual Understanding
- Understands role-specific requirements
- Recognizes transferable skills
- Evaluates cultural fit indicators

### Actionable Insights
- Specific improvement suggestions
- Skills gap identification
- Career development recommendations

## 🔍 Project Structure

```
resume-evaluator-ai/
├── frontend/                 # React TypeScript application
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── sample_data/     # Example resumes and job descriptions
│   │   └── App.tsx          # Main application component
│   └── package.json         # Frontend dependencies
├── backend/
│   └── express-llm/         # Express.js API server
│       ├── controller/      # Business logic
│       ├── app.js           # Server entry point
│       ├── routes.js        # API endpoints
│       └── .env             # Environment variables
├── playbook/                # Educational materials
│   └── ResumeEvaluator.ipynb # Jupyter notebook tutorial
└── README.md                # This file
```

## 🚀 API Endpoints

### POST `/llm-chat/generate-score`
Evaluates resumes and generates scores.

**Request Body**:
```json
{
  "companyName": "Google",
  "roleName": "Software Engineer",
  "jobDescription": "We are looking for...",
  "resumeText": "John Doe\nSoftware Engineer..."
}
```

**Response**:
```json
{
  "message": "Score generated",
  "data": {
    "score": "8",
    "name": "John Doe",
    "justification": "Strong technical skills...",
    "resumeSummary": "Experienced software engineer..."
  }
}
```

### POST `/llm-chat/generate-suggestion`
Provides improvement suggestions based on evaluation.

**Request Body**:
```json
{
  "score": "7",
  "resumeSummary": "Experienced developer...",
  "jobDescription": "We are looking for..."
}
```

## 🎨 UI Features

- **Material-UI Design**: Modern, responsive interface
- **Split View Layout**: Input on left, results on right
- **Real-time Updates**: Streaming responses displayed as generated
- **Error Handling**: Graceful error messages and retry options
- **Dark Mode Support**: Automatic theme detection

## 🔒 Security Considerations

- API keys stored in environment variables
- CORS enabled for frontend-backend communication
- Input validation and sanitization
- Rate limiting recommended for production

## 🚀 Advanced Features

### Batch Processing
- Evaluate multiple resumes in parallel
- Export results to CSV or JSON
- Generate comparison reports

### Customization Options
- Adjust scoring criteria via prompts
- Add custom evaluation metrics
- Integrate with ATS systems

### Performance Optimization
- Response streaming for better UX
- Caching for repeated evaluations
- Lazy loading for large datasets

## 🤝 Contributing

This project demonstrates AI-powered recruitment technology and is designed for:
- Learning modern full-stack development with AI
- Prototyping HR tech solutions
- Research in automated candidate evaluation

Project By:
Thangavel Jishnuanandh (NVIDIA Student Ambassador), Darren Tan (NVIDIA), Aik Beng Ng (NVIDIA), Simon See (NVIDIA)

An NVAITC APS project (NVIDIA).

## 📄 License

This project is licensed under the MIT License - see the repository's [LICENSE](../../LICENSE) file for details.
