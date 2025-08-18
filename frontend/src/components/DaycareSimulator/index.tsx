import React from 'react';
import { useSimulatorContext } from '../../contexts/SimulatorContext';
import WelcomeScreen from './WelcomeScreen';
import InputForm from './InputForm';
import InsightsDashboard from './InsightsDashboard';
import NextSteps from './NextSteps';

const DaycareSimulator: React.FC = () => {
  const { currentStep } = useSimulatorContext();

  const renderStep = () => {
    switch (currentStep) {
      case 0: return <WelcomeScreen />;
      case 1: return <InputForm />;
      case 2: return <InsightsDashboard />;
      case 3: return <NextSteps />;
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