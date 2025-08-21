import React, { useEffect } from 'react';
import { useSimulatorContext } from '../../contexts/SimulatorContext';
import WelcomeScreen from './WelcomeScreen';
import InputForm from './InputForm';
import InsightsDashboard from './InsightsDashboard';
import NextSteps from './NextSteps';
import ProFormaDashboard from './ProFormaDashboard';

const DaycareSimulator: React.FC = () => {
  const { currentStep } = useSimulatorContext();
  useEffect(() => {
    console.log('Current step:', currentStep);
  }, [currentStep]);

  const renderStep = () => {
    switch (currentStep) {
      case 0: return <WelcomeScreen />;
      case 1: return <InputForm />;
      case 2: return <InsightsDashboard />;
      case 3: return <NextSteps />;
      case 4: return <ProFormaDashboard />;
      default: return <WelcomeScreen />;
    }
  };

  return (
    <div className="simulator-page">
      {renderStep()}
    </div>
  );
};

export default DaycareSimulator;