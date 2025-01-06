import { useMemo } from 'react';
import { ApiResponse } from '../types/api';
import { UserPerformance, TradeThought } from '../types/api';

export function useUserData(
  userId: string | null,
  apiResponse: ApiResponse | null
) {
  return useMemo(() => {
    if (!userId || !apiResponse) {
      return {
        performance: null,
        thoughts: [],
      };
    }

    const userName = Object.keys(apiResponse.people).find(
      name => name.toLowerCase() === userId
    );

    if (!userName) {
      return {
        performance: null,
        thoughts: [],
      };
    }

    return {
      performance: apiResponse.people_performance[userName],
      thoughts: apiResponse.people_thoughts[userName] || [],
    };
  }, [userId, apiResponse]);
}