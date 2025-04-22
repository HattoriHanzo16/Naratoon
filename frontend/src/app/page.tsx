"use client";

import { useState } from 'react';
import ComicDisplay from '@/components/ComicDisplay'; // Import the new component

// Define the types based on the backend API response
interface ComicPanelResponse {
  panel_number: number;
  scene_description: string;
  panel_text?: string; // Adding panel_text as optional field
  image_url: string;
}

interface ProjectResponse {
  id: number;
  title: string;
  story_text: string;
  created_at: string; // Use string for simplicity, or Date and parse
  panels: ComicPanelResponse[];
}

export default function Home() {
  const [title, setTitle] = useState('');
  const [storyText, setStoryText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // Use the defined type for the result state
  const [comicResult, setComicResult] = useState<ProjectResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setComicResult(null);

    try {
      const response = await fetch('/api/generate-comic/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title, story_text: storyText }),
      });

      if (!response.ok) {
        // Attempt to parse error detail from backend
        let errorDetail = 'Failed to generate comic';
        try {
          const errorData = await response.json();
          errorDetail = errorData.detail || errorDetail;
        } catch (jsonError) {
          // If parsing error fails, use the status text
          errorDetail = response.statusText || errorDetail;
        }
        throw new Error(errorDetail);
      }

      // Parse the successful response
      const result: ProjectResponse = await response.json();
      setComicResult(result);
      console.log('Generated Comic:', result);

    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-gradient-to-br from-indigo-100 via-purple-100 to-pink-100">
      {/* Add global styles needed for the animation */}
      <style jsx global>{`
        @keyframes progress-animation {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        .animate-progress {
          animation: progress-animation 2s linear infinite;
          transform-origin: left;
        }
      `}</style>

      <div className="w-full max-w-2xl bg-white rounded-xl shadow-xl p-8 md:p-12">
        <h1 className="text-4xl md:text-5xl font-bold text-center mb-8 bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-pink-600">
          NaraToon
        </h1>

        {/* Show Loading State OR Form */} 
        {loading ? (
          <div className="text-center py-12">
            <p className="text-lg font-medium text-gray-700 mb-4">Generating your comic...</p>
            <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
              <div className="bg-gradient-to-r from-cyan-500 to-blue-500 h-2.5 rounded-full animate-progress"></div>
            </div>
            <p className="text-sm text-gray-500 mt-3">This might take a minute or two.</p>
          </div>
        ) : !comicResult ? (
          // Original Form
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                Title
              </label>
              <input
                type="text"
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-cyan-500 focus:border-cyan-500 transition duration-150 ease-in-out text-gray-900"
                placeholder="Enter your comic title"
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="storyText" className="block text-sm font-medium text-gray-700 mb-1">
                Story Text
              </label>
              <textarea
                id="storyText"
                value={storyText}
                onChange={(e) => setStoryText(e.target.value)}
                required
                rows={8}
                className="w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-cyan-500 focus:border-cyan-500 transition duration-150 ease-in-out text-gray-900"
                placeholder="Enter your story here..."
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className={`w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white transition duration-150 ease-in-out ${
                loading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-cyan-500'
              }`}
            >
              {loading ? (
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              ) : (
                'Generate Comic'
              )}
            </button>
          </form>
        ) : null} {/* End of Loading/Form block */}

        {/* Display Error Messages */}
        {error && (
          <div className="mt-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-md">
            <p><strong>Error:</strong> {error}</p>
          </div>
        )}

        {/* Display Comic Results using the new component */}
        {comicResult && (
           <ComicDisplay panels={comicResult.panels} projectId={comicResult.id} />
        )}

        {/* Optional: Add a button to generate a new comic */}
        {comicResult && (
           <button
             onClick={() => {
               setComicResult(null); // Reset result
               setTitle(''); // Clear form
               setStoryText('');
               setError(null);
             }}
             className="mt-6 w-full flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
           >
             Generate Another Comic
           </button>
        )}

      </div>
    </main>
  );
}
