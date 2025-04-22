![NaraToon Logo](public/logo.png)

# NaraToon: Text-to-Comic Generator

Transform your stories into visually engaging comic strips using AI technology. NaraToon automatically analyzes your narrative, breaks it down into panels, and generates custom illustrations to bring your stories to life.

[Watch Demo Video](https://youtu.be/TaEqlmV5eg8)

## Features

- **Text-to-Comic Conversion**: Convert any text story into a multi-panel comic strip
- **AI-Powered Scene Analysis**: Intelligent breakdown of narrative into logical comic panels
- **Custom Illustrations**: Generate unique images for each comic panel using DALL-E
- **Panel Text Generation**: Automatically extracts or generates appropriate text for each panel
- **Export Options**: Save your comics as images or PDF files
- **Project Management**: Save, view, and edit your comic projects

## Tech Stack
 
### Frontend
- **Framework**: Next.js 15.3.0 with Turbopack
- **UI Library**: React 19.0.0
- **Styling**: TailwindCSS
- **Export Utilities**: html2canvas, jspdf

### Backend
- **API Framework**: FastAPI 0.104.1
- **Server**: Uvicorn 0.24.0
- **Database ORM**: SQLAlchemy 2.0.23
- **Database**: SQLite
- **AI Integration**: OpenAI API (GPT for text analysis, DALL-E for image generation)
- **Authentication**: Python-JOSE, Passlib, Bcrypt

## Setup Instructions

### Prerequisites

- Node.js (v18 or higher)
- Python (v3.8 or higher)
- OpenAI API key with access to GPT and DALL-E

### Installation

#### Manual Setup

1. Clone the repository:
```bash
git clone https://github.com/HattoriHanzo16/naratoon.git
cd naratoon
```

2. Frontend setup:
```bash
cd frontend
npm install
npm run dev
```

3. Backend setup:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

4. Set up environment variables:
- Create a `.env` file in the backend directory
- Add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

5. Run the backend server:
```bash
cd backend
uvicorn app.main:app --reload
```

#### Using Makefile (Recommended)

A Makefile is provided to simplify setup and running processes:

```bash
# Set up both frontend and backend
make setup

# Run both servers simultaneously
make run

# Other useful commands
make stop     # Stop all running servers
make clean    # Clean up generated files and dependencies
```

For more options, run `make help` to see all available commands.

## Usage

1. Start both the frontend and backend servers using the instructions above
2. Open your browser and navigate to http://localhost:3000
3. Enter your story title and text in the provided form
4. Click "Generate Comic" to process your story
5. View, download, or share your generated comic

## Project Structure

```
naratoon/
├── frontend/                # Next.js frontend application
│   ├── src/
│   │   ├── app/             # Next.js app router pages
│   │   └── components/      # React components
│   ├── public/              # Static assets
│   └── package.json         # Frontend dependencies
├── backend/                 # FastAPI backend application
│   ├── app/
│   │   ├── api/             # API endpoints
│   │   ├── models/          # Data models
│   │   ├── services/        # Business logic services
│   │   ├── database.py      # Database connection setup
│   │   └── main.py          # Application entry point
│   ├── requirements.txt     # Backend dependencies
│   └── .env                 # Environment variables (create this file)
└── database/                # SQLite database files
    └── naratoon.db          # Main database file
```

## API Endpoints

- `POST /api/generate-comic/`: Generate a new comic from story text
- `GET /api/projects/`: List all comic projects
- `GET /api/projects/{project_id}`: Get details for a specific project

## Image Handling

NaraToon generates images using DALL-E and stores the image URLs in the database. To handle the direct integration with DALL-E:

1. The application uses the OpenAI API to generate images from scene descriptions
2. Images are returned as URLs from DALL-E and stored in the database
3. To avoid CORS issues when displaying images, consider implementing one of these approaches:
   - Store generated images locally in your backend and serve them directly
   - Configure proper CORS headers on your server
   - Use a dedicated image hosting service with appropriate CORS policies

## Acknowledgments

- Built with OpenAI's GPT and DALL-E APIs
- Inspired by the intersection of storytelling and visual arts 