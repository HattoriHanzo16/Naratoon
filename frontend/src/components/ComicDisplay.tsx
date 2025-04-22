import { useState, useRef, useEffect } from 'react';
import Image from 'next/image';

// Define the types based on the backend API response
interface ComicPanelResponse {
  panel_number: number;
  scene_description: string;
  panel_text?: string; // Adding panel_text as optional field
  image_url: string;
}

interface ComicDisplayProps {
  panels: ComicPanelResponse[];
  projectId?: number; // Optional project ID
}

const BACKEND_URL = 'http://localhost:8000';

export default function ComicDisplay({ panels, projectId }: ComicDisplayProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [imageError, setImageError] = useState<Record<number, boolean>>({});
  const comicContainerRef = useRef<HTMLDivElement>(null);
  const panelImageRef = useRef<HTMLDivElement>(null);

  if (!panels || panels.length === 0) {
    return <p className="text-center text-gray-500">No panels to display.</p>;
  }

  const currentPanel = panels[currentIndex];
  
  // Get the full image URL
  const getImageUrl = (relativeUrl: string) => {
    // If the URL is already absolute (e.g., https://...), return it as is
    if (relativeUrl.startsWith('http://') || relativeUrl.startsWith('https://')) {
      return relativeUrl;
    }
    
    // Fix: Don't use proxy-image endpoint for local static files
    return `${BACKEND_URL}${relativeUrl}`;
  };

  const handleImageError = (panelNumber: number) => {
    console.error(`Failed to load image for panel ${panelNumber}`);
    setImageError(prev => ({
      ...prev,
      [panelNumber]: true
    }));
  };

  const goToPrevious = () => {
    setCurrentIndex((prevIndex) =>
      prevIndex === 0 ? panels.length - 1 : prevIndex - 1
    );
  };

  const goToNext = () => {
    setCurrentIndex((prevIndex) =>
      prevIndex === panels.length - 1 ? 0 : prevIndex + 1
    );
  };

  const downloadComic = async () => {
    if (typeof window !== 'undefined') {
      try {
        // Dynamically import html2canvas and jspdf
        const html2canvas = (await import('html2canvas')).default;
        const { jsPDF } = await import('jspdf');
        
        if (comicContainerRef.current) {
          const canvas = await html2canvas(comicContainerRef.current);
          const imgData = canvas.toDataURL('image/png');
          
          const pdf = new jsPDF({
            orientation: 'landscape',
            unit: 'px'
          });
          
          // Calculate dimensions to maintain aspect ratio
          const imgProps = pdf.getImageProperties(imgData);
          const pdfWidth = pdf.internal.pageSize.getWidth();
          const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;
          
          pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
          pdf.save(`comic-${projectId || 'download'}.pdf`);
        }
      } catch (error) {
        console.error('Error downloading comic:', error);
        alert('Failed to download comic. Please try again later.');
      }
    }
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Comic Preview</h2>
      
      <div className="flex justify-between mb-4">
        <button
          onClick={goToPrevious}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Previous
        </button>
        <span className="self-center">
          Panel {currentIndex + 1} of {panels.length}
        </span>
        <button
          onClick={goToNext}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Next
        </button>
      </div>
      
      <div 
        ref={comicContainerRef}
        className="comic-container bg-gray-100 p-4 rounded-lg mb-4"
      >
        {/* Panel content */}
        <div className="panel-content flex flex-col space-y-4">
          <div className="panel-description">
            <h3 className="text-xl font-semibold mb-2">Scene Description:</h3>
            <p>{currentPanel.scene_description}</p>
          </div>
          
          {/* Image container */}
          <div
            ref={panelImageRef}
            className="panel-image-container relative h-96 w-full bg-gray-200 rounded overflow-hidden"
          >
            {/* Image */}
            {imageError[currentPanel.panel_number] ? (
              <div className="flex h-full w-full items-center justify-center bg-gray-300">
                <p className="text-gray-600">Image failed to load</p>
              </div>
            ) : (
              <img
                src={getImageUrl(currentPanel.image_url)}
                alt={`Comic panel ${currentPanel.panel_number}`}
                className="object-contain w-full h-full"
                onError={() => handleImageError(currentPanel.panel_number)}
              />
            )}
          </div>
          
          {/* Panel text */}
          {currentPanel.panel_text && (
            <div className="panel-text bg-white p-3 rounded border border-gray-300">
              <h3 className="text-xl font-semibold mb-2">Panel Text:</h3>
              <p>{currentPanel.panel_text}</p>
            </div>
          )}
        </div>
      </div>
      
      <div className="flex justify-center">
        <button
          onClick={downloadComic}
          className="px-6 py-2 bg-green-500 text-white rounded hover:bg-green-600"
        >
          Download Comic
        </button>
      </div>
    </div>
  );
} 