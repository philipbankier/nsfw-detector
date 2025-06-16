import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';

// Mock fetch
global.fetch = jest.fn();

describe('App Component', () => {
  beforeEach(() => {
    // Reset fetch mock before each test
    fetch.mockClear();
  });

  test('renders upload interface', () => {
    render(<App />);
    expect(screen.getByText(/NSFW Video Analyzer/i)).toBeInTheDocument();
    expect(screen.getByText(/Upload a video to analyze/i)).toBeInTheDocument();
  });

  test('handles file selection', async () => {
    render(<App />);
    
    const file = new File(['test video content'], 'test.mp4', { type: 'video/mp4' });
    const input = screen.getByLabelText(/browse/i);
    
    await userEvent.upload(input, file);
    
    expect(screen.getByText(/Selected file: test.mp4/i)).toBeInTheDocument();
  });

  test('shows error for invalid file type', async () => {
    render(<App />);
    
    const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
    const input = screen.getByLabelText(/browse/i);
    
    await userEvent.upload(input, file);
    
    expect(screen.getByText(/Please select a valid video file/i)).toBeInTheDocument();
  });

  test('handles successful video analysis', async () => {
    const mockResult = {
      method: 'gemini',
      status: 'safe',
      categories: ['other'],
      severity: 0,
      description: 'Safe content suitable for all audiences'
    };

    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockResult)
      })
    );

    render(<App />);
    
    // Upload file
    const file = new File(['test video content'], 'test.mp4', { type: 'video/mp4' });
    const input = screen.getByLabelText(/browse/i);
    await userEvent.upload(input, file);
    
    // Click analyze button
    const analyzeButton = screen.getByText(/Analyze Video/i);
    await userEvent.click(analyzeButton);
    
    // Wait for results
    await waitFor(() => {
      expect(screen.getByText(/Analysis Result/i)).toBeInTheDocument();
      expect(screen.getByText(/Safe/i)).toBeInTheDocument();
      expect(screen.getByText(/other/i)).toBeInTheDocument();
    });
  });

  test('handles analysis error', async () => {
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: false,
        json: () => Promise.resolve({ detail: 'Analysis failed' })
      })
    );

    render(<App />);
    
    // Upload file
    const file = new File(['test video content'], 'test.mp4', { type: 'video/mp4' });
    const input = screen.getByLabelText(/browse/i);
    await userEvent.upload(input, file);
    
    // Click analyze button
    const analyzeButton = screen.getByText(/Analyze Video/i);
    await userEvent.click(analyzeButton);
    
    // Wait for error
    await waitFor(() => {
      expect(screen.getByText(/Analysis failed/i)).toBeInTheDocument();
    });
  });

  test('handles drag and drop', async () => {
    render(<App />);
    
    const dropZone = screen.getByText(/Drag and drop a video file here/i).parentElement;
    const file = new File(['test video content'], 'test.mp4', { type: 'video/mp4' });
    
    // Simulate drag over
    fireEvent.dragOver(dropZone);
    expect(dropZone).toHaveClass('border-blue-500');
    
    // Simulate drop
    fireEvent.drop(dropZone, {
      dataTransfer: {
        files: [file]
      }
    });
    
    expect(screen.getByText(/Selected file: test.mp4/i)).toBeInTheDocument();
  });

  test('displays multiple categories correctly', async () => {
    const mockResult = {
      method: 'joycaption-whisper-grok',
      status: 'nsfw',
      categories: ['pornography', 'violence'],
      severity: 4,
      description: 'Contains explicit content and graphic violence'
    };

    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockResult)
      })
    );

    render(<App />);
    
    // Upload and analyze
    const file = new File(['test video content'], 'test.mp4', { type: 'video/mp4' });
    const input = screen.getByLabelText(/browse/i);
    await userEvent.upload(input, file);
    
    const analyzeButton = screen.getByText(/Analyze Video/i);
    await userEvent.click(analyzeButton);
    
    // Check categories
    await waitFor(() => {
      expect(screen.getByText(/pornography/i)).toBeInTheDocument();
      expect(screen.getByText(/violence/i)).toBeInTheDocument();
      expect(screen.getByText(/Extreme/i)).toBeInTheDocument();
    });
  });
}); 