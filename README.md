# ManimGen - AI-Powered Animation Generator

Transform text prompts into stunning mathematical animations using AI and Manim.

![ManimGen Preview](https://via.placeholder.com/800x400?text=ManimGen+Preview)

## Features

- 🤖 **AI-Powered Generation** - Describe animations in plain English
- 🎬 **Scene-Based Editing** - Build complex videos with individual scenes
- 🎤 **Voice-Over Integration** - Add narration with audio upload
- 💻 **Code Visibility** - View and edit generated Python code
- 📱 **Timeline Editor** - Drag-and-drop scene arrangement
- 🚀 **One-Click Export** - Compile and download your video

## Tech Stack

- **Frontend**: Next.js 15, React, TypeScript, Tailwind CSS, Framer Motion
- **Backend**: FastAPI, Python 3.11
- **AI**: OpenRouter API (supports Claude, GPT-4, Gemini, and more)
- **Animation**: Manim Community Edition
- **Video Processing**: FFmpeg

## Prerequisites

- Node.js 18+
- Python 3.11+
- FFmpeg
- Manim (with LaTeX for math rendering)

## Quick Start

### 1. Clone and Install

```bash
# Install frontend dependencies
npm install

# Install backend dependencies
cd backend
pip install -r requirements.txt
pip install manim
```

### 2. Configure Environment

```bash
# Backend
cp backend/env.template backend/.env
# Edit backend/.env and add your OPENROUTER_API_KEY

# Frontend
cp env.template .env.local
```

### 3. Get OpenRouter API Key

1. Go to [OpenRouter](https://openrouter.ai/keys)
2. Create a new API key
3. Add it to `backend/.env`
4. Optionally set your preferred model (defaults to Claude 3.5 Sonnet)

### 4. Run Development Servers

```bash
# Terminal 1 - Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000)

## Project Structure

```
├── src/
│   ├── app/
│   │   ├── page.tsx          # Landing page
│   │   ├── editor/
│   │   │   └── page.tsx      # Main editor
│   │   └── globals.css       # Global styles
│   ├── components/
│   │   ├── PromptInput.tsx   # Prompt input with suggestions
│   │   ├── VideoPreview.tsx  # Video player component
│   │   ├── Timeline.tsx      # Drag-drop scene timeline
│   │   ├── CodeEditor.tsx    # Python code viewer/editor
│   │   └── VoiceOver.tsx     # Audio upload component
│   └── lib/
│       └── api.ts            # API client
├── backend/
│   ├── main.py               # FastAPI app entry
│   ├── config.py             # Configuration
│   ├── routers/
│   │   ├── projects.py       # Project CRUD
│   │   ├── scenes.py         # Scene management
│   │   ├── render.py         # Video rendering
│   │   └── audio.py          # Audio handling
│   └── services/
│       ├── llm_service.py    # OpenRouter API integration
│       ├── code_validator.py # Manim code validation
│       └── render_service.py # Manim execution
└── docker/
    ├── Dockerfile.backend    # Backend container
    └── Dockerfile.frontend   # Frontend container
```

## Usage

### Creating Animations

1. **Enter a Prompt**: Describe what you want to animate
   - "Create a circle that transforms into a square"
   - "Visualize binary search on a sorted array"
   - "Show data flow from client to server"

2. **Generate**: AI creates Manim code for your animation

3. **Render**: Click "Render" to generate the video

4. **Arrange**: Use the timeline to order multiple scenes

5. **Export**: Download your final video with optional voice-over

### Example Prompts

| Prompt | Description |
|--------|-------------|
| "Show the Pythagorean theorem proof" | Animated geometric proof |
| "Visualize quicksort algorithm" | Step-by-step sorting animation |
| "Animate a neural network forward pass" | ML concept visualization |
| "Create client-server-database flow" | Architecture diagram animation |

## Deployment on Railway

### Backend Deployment

1. Create a new Railway project
2. Add a new service from GitHub
3. Set the Dockerfile path: `docker/Dockerfile.backend`
4. Add environment variables:
   - `OPENROUTER_API_KEY`
   - `OPENROUTER_MODEL` (optional, defaults to claude-3.5-sonnet)
   - `FRONTEND_URL` (your frontend URL)

### Frontend Deployment

1. Add another service from GitHub
2. Set the Dockerfile path: `docker/Dockerfile.frontend`
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL` (your backend URL)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/projects/` | Create project |
| GET | `/api/projects/` | List projects |
| POST | `/api/scenes/` | Create scene from prompt |
| POST | `/api/render/scene/{id}` | Render a scene |
| POST | `/api/render/export/{id}` | Export full project |
| POST | `/api/audio/upload/{id}` | Upload voice-over |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [Manim Community](https://www.manim.community/) - Animation engine
- [3Blue1Brown](https://www.3blue1brown.com/) - Original Manim creator
- [OpenRouter](https://openrouter.ai/) - AI model gateway
