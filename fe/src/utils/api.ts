import { mockStats } from './mockData';

export async function fetchStats() {
  try {
    const response = await fetch('http://127.0.0.1:8000/stats');
    const data = await response.json();
    
    if (data.status === 'success') {
      return { data: data.stats, error: null };
    }
    throw new Error('Failed to fetch stats');
  } catch (err) {
    console.warn('Using mock data due to API error:', err);
    return { data: mockStats, error: null };
  }
}

export async function queryAssistant(query: string, role: string) {
  try {
    const response = await fetch('http://127.0.0.1:8000/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, role }),
    });
    const data = await response.json();
    
    if (data.status === 'success') {
      return { response: data.response, error: null };
    }
    throw new Error('Failed to get response');
  } catch (err) {
    return { 
      response: "I apologize, but I'm currently offline. Please try again later.",
      error: 'Failed to send message'
    };
  }
}