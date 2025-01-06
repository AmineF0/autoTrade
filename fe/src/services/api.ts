import { ApiResponse } from '../types/api';
import { mockApiResponse } from './mockData';

const API_BASE_URL = 'http://localhost:8000';

export async function fetchTradingData(): Promise<ApiResponse> {
  try {
    const response = await fetch(API_BASE_URL);
    if (!response.ok) {
      // If API fails, return mock data
      console.warn('API unavailable, using mock data');
      return mockApiResponse;
    }
    return response.json();
  } catch (error) {
    console.warn('API error, using mock data:', error);
    return mockApiResponse;
  }
}