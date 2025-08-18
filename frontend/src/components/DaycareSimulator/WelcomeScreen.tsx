import React from 'react';
import { Button, Card, Typography, Row, Col } from 'antd';
import { useSimulatorContext } from '../../contexts/SimulatorContext';

const { Title, Paragraph } = Typography;

const WelcomeScreen: React.FC = () => {
  const { setCurrentStep } = useSimulatorContext();

  return (
    <div className="welcome-container">
      <Card bordered={false} className="welcome-card">
        <Title level={2} style={{ color: '#1890ff' }}>
          Center Operations Simulator
        </Title>
        <Title level={4} type="secondary" style={{ marginTop: '8px' }}>
          Simulate cash flow, budgeting, staffing, and financial events
        </Title>
        
        <div style={{ margin: '40px 0' }}>
          <Row gutter={[24, 24]}>
            <Col xs={24} md={12}>
              <div className="feature-card">
                <div className="feature-icon" style={{ backgroundColor: '#e6f7ff' }}>
                  <span>💰</span>
                </div>
                <h3>Financial Analysis</h3>
                <p>Calculate net income, break-even points, and expense ratios</p>
              </div>
            </Col>
            <Col xs={24} md={12}>
              <div className="feature-card">
                <div className="feature-icon" style={{ backgroundColor: '#f6ffed' }}>
                  <span>👥</span>
                </div>
                <h3>Staffing Optimization</h3>
                <p>Determine optimal staff levels based on enrollment</p>
              </div>
            </Col>
            <Col xs={24} md={12}>
              <div className="feature-card">
                <div className="feature-icon" style={{ backgroundColor: '#fff2e8' }}>
                  <span>📈</span>
                </div>
                <h3>Growth Planning</h3>
                <p>Simulate expansion scenarios and financial impacts</p>
              </div>
            </Col>
            <Col xs={24} md={12}>
              <div className="feature-card">
                <div className="feature-icon" style={{ backgroundColor: '#f9f0ff' }}>
                  <span>🛡️</span>
                </div>
                <h3>Risk Assessment</h3>
                <p>Evaluate financial resilience against unexpected events</p>
              </div>
            </Col>
          </Row>
        </div>
        
        <Paragraph style={{ fontSize: '16px', marginBottom: '40px' }}>
          This AI-powered tool helps daycare center owners understand their financial health, 
          optimize staffing, and plan for growth with personalized insights and recommendations.
        </Paragraph>
        
        <Button 
          type="primary" 
          size="large" 
          onClick={() => setCurrentStep(1)}
          style={{ 
            padding: '0 40px', 
            height: '50px', 
            fontSize: '18px',
            fontWeight: 'bold'
          }}
        >
          Get Started
        </Button>
      </Card>
    </div>
  );
};

export default WelcomeScreen;