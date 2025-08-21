import React, { createContext, useState, useContext, ReactNode, useEffect } from 'react';
import { FormData, InsightData, Recommendations } from '../types/simulatorTypes';
import { getRecommendations } from '../services/api';


interface SimulatorContextType {
  formData: FormData;
  setFormData: React.Dispatch<React.SetStateAction<FormData>>;
  currentStep: number;
  setCurrentStep: (step: number) => void;
  insights: InsightData | null;
  setInsights: React.Dispatch<React.SetStateAction<InsightData | null>>;
  recommendations: Recommendations | null;
  setRecommendations: React.Dispatch<React.SetStateAction<Recommendations | null>>;
  userEmail: string;
  recommendationsLoading: boolean;
  fetchRecommendations: () => Promise<void>;
  dashboardData: any;
  setDashboardData: React.Dispatch<React.SetStateAction<any>>; // Add this
}

const defaultFormData: FormData = {
  businessName: '',
  revenueSources: [
    { id: '1', sourceName: '', monthlyAmount: 0, tag: '' },
    { id: '2', sourceName: '', monthlyAmount: 0, tag: '' }
  ],
  employees: [
    { id: '1', expenseName: '', hoursPerMonth: 0,  monthlyAmount: 0, type: 'Monthly' },
  ],
  facilities: [
    { id: '1', expenseName: '', monthlyAmount: 0, type: 'Monthly' }
  ],
  administrative: [
    { id: '1', expenseName: '', monthlyAmount: 0, type: 'Monthly' }
  ],
  supplies: [
    { id: '1', expenseName: '', monthlyAmount: 0, type: 'Monthly' }
  ],
  classrooms: [
    { id: '1', name: '', capacity: 0, ratio: 0, avgStudents: 0}
  ],
  operatingHours: 0,
  operatingDays: 0,
  goals: [
    { id: '1', goal: 'Increase Revenue', targetPercentage: 0},
    { id: '2', goal: 'Reduce Expense', targetPercentage: 0},
    { id: '3', goal: 'Improve Classroom Utilization', targetPercentage: 0}
  ]
};

const SimulatorContext = createContext<SimulatorContextType | undefined>(undefined);

export const SimulatorProvider: React.FC<{children: ReactNode; email: string}> = ({ children, email }) => {
  const [formData, setFormData] = useState<FormData>(defaultFormData);
  const [currentStep, setCurrentStep] = useState(0);
  const [insights, setInsights] = useState<InsightData | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendations | null>(null);
  const [userEmail, setUserEmail] = useState(email);
  const [recommendationsLoading, setRecommendationsLoading] = useState(false);
  const [dashboardData, setDashboardData] = useState<any>(null); // Add this

  useEffect(() => {
      setUserEmail(email); // update state when prop changes
    }, [email]);
  
  const fetchRecommendations = async () => {
    try {
      const recs = await getRecommendations();
      setRecommendations(recs);
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
      // Set default recommendations if API fails
      setRecommendations({
        recommendations: [
          "Review your financial reports regularly",
          "Optimize staff scheduling based on enrollment patterns",
          "Explore new revenue streams like after-school programs"
        ]
      });
    }
    finally {
      setRecommendationsLoading(false);
    }
  };

  return (
    <SimulatorContext.Provider value={{
      formData,
      setFormData,
      currentStep,
      setCurrentStep,
      insights,
      setInsights,
      recommendations,
      setRecommendations,
      dashboardData,
      setDashboardData,
      userEmail,
      fetchRecommendations,
      recommendationsLoading
    }}>
      {children}
    </SimulatorContext.Provider>
  );
};

export const useSimulatorContext = () => {
  const context = useContext(SimulatorContext);
  if (!context) throw new Error('useSimulatorContext must be used within SimulatorProvider');
  return context;
};