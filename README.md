# ByteBond Hackathon Project - Legal Document Assistant

A comprehensive AI-powered legal document analysis platform that helps users understand, analyze, and interact with legal documents through intelligent question-answering and clause extraction.

## 🚀 Features
- **Multi-Format Document Support**: Upload PDF, DOCX, TXT, and image files
- **AI-Powered Analysis**: Advanced document understanding using Google Gemini AI
- **Interactive Q&A**: Ask questions about your documents and get intelligent responses
- **Legal Clause Extraction**: Automatically identify and analyze legal clauses
- **Risk Assessment**: Evaluate potential risks and gaps in legal documents
- **OCR Support**: Extract text from scanned documents and images
- **Responsive Design**: Modern, mobile-first interface with glassmorphism effects
- **Real-time Processing**: Asynchronous document analysis with progress indicators

## 🛠️ Technology Stack
### Backend Technologies
- **Python** - Primary backend language
- **FastAPI** - Modern web framework for building APIs
- **Uvicorn** - ASGI server for running FastAPI
- **Google Generative AI (Gemini)** - Document analysis and content generation
  - Models: gemini-2.0-flash and gemini-2.5-flash-preview-05-20
- **PyMuPDF (fitz)** - PDF text extraction and processing
- **pytesseract** - OCR for extracting text from images and scanned documents
- **python-docx** - Microsoft Word document processing
- **Pillow (PIL)** - Image processing and manipulation

### Frontend Technologies
- **HTML5** - Document structure and semantic markup
- **CSS3** - Advanced styling with modern features
- **JavaScript (ES6+)** - Interactive functionality and API communication
- **Tailwind CSS** - Utility-first CSS framework
- **Tesseract.js** - Client-side OCR processing
- **Font Awesome** - Icon library for UI elements

### External Services
- **Google Fonts** - Typography (Montserrat, Inter fonts)
- **Google Generative AI API** - Direct API calls from frontend

## 📁 Project Structure
```
ByteBondHackathonProject/
├── .vscode/                 # VS Code configuration
├── __pycache__/            # Python cache files
├── backend.py              # FastAPI backend server
├── gemm.html              # AI chat interface
├── index.html             # Main dashboard/homepage
├── login.html             # User authentication page
├── uploadDoc.html         # Document upload interface
└── README.md              # Project documentation
```

## 🚀 Getting Starte
### Prerequisites
- Python 3.8 or higher
- Google Generative AI API key
- Tesseract OCR installed on your system

### Installation
1. **Clone the repository**
   ```bash
   git clone https://github.com/VEDIKA-9299/ByteBondHackathonProject.git
   cd ByteBondHackathonProject
   ```

2. **Install Python dependencies**
   ```bash
   pip install fastapi uvicorn google-generativeai PyMuPDF pytesseract python-docx Pillow python-dotenv
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_google_generative_ai_api_key_here
   ```

4. **Install Tesseract OCR**
   - **Windows**: Download from [GitHub Tesseract releases](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Ubuntu/Debian**: `sudo apt-get install tesseract-ocr`

### Running the Application
1. **Start the backend server**
   ```bash
   python backend.py
   ```
   The server will start on `http://localhost:8001`

2. **Access the application**
   Open your web browser and navigate to `http://localhost:8001`

## 🎯 User Journey
### 1. Login Page (`login.html`)
- User authentication interface
- Modern gradient design with glassmorphism effects
- Secure login functionality

### 2. Main Dashboard (`index.html`)
- Home page with feature overview
- Navigation to document upload
- "Try for Free" call-to-action
- Responsive grid layout

### 3. Document Upload (`uploadDoc.html`)
- Drag-and-drop file upload interface
- Multi-format support (PDF, DOCX, TXT, images)
- File validation and size restrictions
- Progress indicators for upload and processing
- "Proceed Further" popup for seamless navigation

### 4. AI Chat Interface (`gemm.html`)
- Interactive Q&A with uploaded documents
- Suggested questions generation
- Real-time responses from Google Gemini AI
- Document analysis and clause extraction

## 🔧 API Endpoints
- `POST /upload` - Upload and analyze documents
- `POST /ask` - Ask questions about uploaded documents
- `GET /health` - Health check endpoint

## 🎨 UI/UX Features
- **Modern Design**: Glassmorphism effects and gradient backgrounds
- **Responsive Layout**: Mobile-first approach with CSS Grid and Flexbox
- **Interactive Elements**: Smooth animations and transitions
- **Accessibility**: Semantic HTML and keyboard navigation support
- **Loading States**: Progress indicators for better user experience

## 🤖 AI Capabilities
- **Document Understanding**: Extract meaning from legal documents
- **Clause Analysis**: Identify and categorize legal clauses
- **Risk Assessment**: Evaluate potential risks and gaps
- **Q&A System**: Answer questions about document content
- **Smart Suggestions**: Generate relevant questions for users

## 📱 Browser Compatibility

- Chrome (recommended)
- Firefox
- Safari
- Edge

## 🚧 Development Status
This project was developed for the ByteBond Hackathon and includes:
- ✅ Complete frontend interface
- ✅ Backend API with FastAPI
- ✅ AI integration with Google Gemini
- ✅ Document processing pipeline
- ✅ Interactive Q&A system

## 📄 License

This project is developed for the ByteBond Hackathon.

## 👥 Contributors

- **VEDIKA-9299**
- **ashmita1603**
- **saileed05**
- **snehavk20**

## 🔗 Links
- **Repository**: [ByteBondHackathonProject](https://github.com/VEDIKA-9299/ByteBondHackathonProject)
- **Live Demo**: `http://localhost:8001` (after setup)

