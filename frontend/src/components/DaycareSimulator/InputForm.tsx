import React, { useState } from 'react';
import { 
  Card, 
  Button, 
  Steps, 
  Row, 
  Col,
  Typography,
  message,
  Input,
  InputNumber
} from 'antd';
import { 
  RevenueSource, 
  ExpenseItem, 
  Classroom, 
  BusinessGoal 
} from '../../types/simulatorTypes';
import { useSimulatorContext } from '../../contexts/SimulatorContext';
import { 
  FormSection, 
  RevenueSources, 
  ExpenseItems, 
  Classrooms, 
  BusinessGoals,
  FileUpload
} from './FormSection';
import UserAvatar from './UserAvatar';
import { saveFormData, uploadFile } from '../../services/api';
import { generateInsights } from '../../services/api';

const { Step } = Steps;
const { Title } = Typography;

const InputForm: React.FC = () => {
  const { 
    formData, 
    setFormData, 
    currentStep, 
    setCurrentStep,
    userEmail,
    setInsights
  } = useSimulatorContext();
  const [loading, setLoading] = useState(false);
  const [fileLoading, setFileLoading] = useState(false);

  // Handlers for revenue sources
  const handleRevenueChange = (id: string, field: keyof RevenueSource, value: any) => {
    setFormData(prev => ({
      ...prev,
      revenueSources: prev.revenueSources.map(source => 
        source.id === id ? { ...source, [field]: value } : source
      )
    }));
  };

  const addRevenueSource = () => {
    setFormData(prev => ({
      ...prev,
      revenueSources: [
        ...prev.revenueSources,
        { id: Date.now().toString(), sourceName: '', monthlyAmount: 0, tag: '' }
      ]
    }));
  };

  const removeRevenueSource = (id: string) => {
    if (formData.revenueSources.length > 1) {
      setFormData(prev => ({
        ...prev,
        revenueSources: prev.revenueSources.filter(source => source.id !== id)
      }));
    }
  };

  // Generic expense handler
  const handleExpenseChange = (
    category: keyof typeof formData, 
    id: string, 
    field: keyof ExpenseItem, 
    value: any
  ) => {
    setFormData(prev => ({
      ...prev,
      [category]: (prev[category] as ExpenseItem[]).map(item => 
        item.id === id ? { ...item, [field]: value } : item
      )
    }));
  };

  const addExpenseItem = (category: keyof typeof formData) => {
    setFormData(prev => ({
      ...prev,
      [category]: [
        ...(prev[category] as ExpenseItem[]),
        { id: Date.now().toString(), expenseName: '', monthlyAmount: 0, type: 'Monthly' }
      ]
    }));
  };

  const removeExpenseItem = (category: keyof typeof formData, id: string) => {
    setFormData(prev => ({
      ...prev,
      [category]: (prev[category] as ExpenseItem[]).filter(item => item.id !== id)
    }));
  };

  // Classroom handlers
  const handleClassroomChange = (id: string, field: keyof Classroom, value: any) => {
    setFormData(prev => ({
      ...prev,
      classrooms: prev.classrooms.map(classroom => 
        classroom.id === id ? { ...classroom, [field]: value } : classroom
      )
    }));
  };

  const addClassroom = () => {
    setFormData(prev => ({
      ...prev,
      classrooms: [
        ...prev.classrooms,
        { id: Date.now().toString(), name: '', capacity: 0, ratio: 0, avgStudents: 0 }
      ]
    }));
  };

  const removeClassroom = (id: string) => {
    if (formData.classrooms.length > 1) {
      setFormData(prev => ({
        ...prev,
        classrooms: prev.classrooms.filter(classroom => classroom.id !== id)
      }));
    }
  };

  // Goal handlers
  const handleGoalChange = (id: string, field: keyof BusinessGoal, value: any) => {
    setFormData(prev => ({
      ...prev,
      goals: prev.goals.map(goal => 
        goal.id === id ? { ...goal, [field]: value } : goal
      )
    }));
  };

  const addGoal = () => {
    setFormData(prev => ({
      ...prev,
      goals: [
        ...prev.goals,
        { id: Date.now().toString(), goal: '', targetPercentage: 0 }
      ]
    }));
  };

  const removeGoal = (id: string) => {
    if (formData.goals.length > 1) {
      setFormData(prev => ({
        ...prev,
        goals: prev.goals.filter(goal => goal.id !== id)
      }));
    }
  };

  // File upload handler
  const handleFileUpload = async (file: File) => {
    setFileLoading(true);
    try {
      await uploadFile(file);
      setFormData(prev => ({ ...prev, uploadedFile: file }));
      message.success('File uploaded successfully');
    } catch (error) {
      message.error('File upload failed');
    } finally {
      setFileLoading(false);
    }
  };

  const handleFileRemove = () => {
    setFormData(prev => ({ ...prev, uploadedFile: null }));
  };

  // Save form data
  const handleSave = async () => {
    setLoading(true);
    try {
      await saveFormData(formData);
      message.success('Data saved successfully');
    } catch (error) {
      message.error('Failed to save data');
    } finally {
      setLoading(false);
    }
  };

  // Generate insights
  const handleGenerateInsights = async () => {
    setLoading(true);
    try {
      const insights = await generateInsights(formData);
      setInsights(insights);  // Update this line
      setCurrentStep(2); // Move to insights page
    } catch (error) {
      message.error('Failed to generate insights');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="simulator-container">
      <Card className="simulator-header-card">
        <div className="header-content">
          <div>
            <Title level={3} style={{ margin: 0, color: '#1890ff' }}>
              Center Operations Simulator
            </Title>
            <p style={{ margin: 0, color: '#666' }}>
              Simulate cash flow, budgeting, staffing, and financial events
            </p>
          </div>
          <UserAvatar email={userEmail} />
        </div>
      </Card>

      <Card className="simulator-card">
        <Steps current={currentStep - 1} className="simulator-steps">
          <Step title="Inputs" description="Operational & Financial Data" />
          <Step title="Insights" description="Simulation Results" />
          <Step title="Next Steps" description="Action Plan" />
        </Steps>

        <div className="form-content">
          <Title level={4} style={{ marginBottom: '24px', color: '#1890ff' }}>
            Operational & Financial Data Entry
          </Title>

          <FormSection 
            title="Business Information" 
            description="Basic information about your daycare center"
          >
            <Row gutter={16}>
              <Col span={24}>
                <Input
                  placeholder="Business Name (e.g., Demo Daycare Center)"
                  value={formData.businessName}
                  onChange={e => setFormData({...formData, businessName: e.target.value})}
                />
              </Col>
            </Row>
          </FormSection>

          <FormSection 
            title="Revenue Sources" 
            description="All income sources for your center"
          >
            <RevenueSources 
              sources={formData.revenueSources}
              onAdd={addRevenueSource}
              onChange={handleRevenueChange}
              onRemove={removeRevenueSource}
            />
          </FormSection>

          <FormSection 
            title="Expenses" 
            description="Breakdown of all operational costs"
          >
            <h4>Employees</h4>
            <ExpenseItems 
              expenses={formData.employees}
              onAdd={() => addExpenseItem('employees')}
              onChange={(id, field, value) => handleExpenseChange('employees', id, field, value)}
              onRemove={(id) => removeExpenseItem('employees', id)}
              showHours={true}
            />

            <h4 style={{ marginTop: '24px' }}>Facilities</h4>
            <ExpenseItems 
              expenses={formData.facilities}
              onAdd={() => addExpenseItem('facilities')}
              onChange={(id, field, value) => handleExpenseChange('facilities', id, field, value)}
              onRemove={(id) => removeExpenseItem('facilities', id)}
            />

            <h4 style={{ marginTop: '24px' }}>Administrative</h4>
            <ExpenseItems 
              expenses={formData.administrative}
              onAdd={() => addExpenseItem('administrative')}
              onChange={(id, field, value) => handleExpenseChange('administrative', id, field, value)}
              onRemove={(id) => removeExpenseItem('administrative', id)}
            />

            <h4 style={{ marginTop: '24px' }}>Supplies</h4>
            <ExpenseItems 
              expenses={formData.supplies}
              onAdd={() => addExpenseItem('supplies')}
              onChange={(id, field, value) => handleExpenseChange('supplies', id, field, value)}
              onRemove={(id) => removeExpenseItem('supplies', id)}
            />
          </FormSection>

          <FormSection 
            title="Classroom & Operational Details" 
            description="Information about your classrooms and operations"
          >
            <Classrooms 
              classrooms={formData.classrooms}
              onAdd={addClassroom}
              onChange={handleClassroomChange}
              onRemove={removeClassroom}
            />

            <h4 style={{ marginTop: '24px' }}>Operating Details</h4>
            <Row gutter={16}>
              <Col span={12}>
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="Operating Hours (daily)"
                  value={formData.operatingHours}
                  onChange={value => setFormData({...formData, operatingHours: value || 0})}
                  min={0}
                  max={24}
                  addonAfter="hours"
                />
              </Col>
              <Col span={12}>
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="Operating Days per Year"
                  value={formData.operatingDays}
                  onChange={value => setFormData({...formData, operatingDays: value || 0})}
                  min={0}
                  max={365}
                  addonAfter="days"
                />
              </Col>
            </Row>
          </FormSection>

          <FormSection 
            title="Business Goals" 
            description="Your financial and operational objectives"
          >
            <BusinessGoals 
              goals={formData.goals}
              onAdd={addGoal}
              onChange={handleGoalChange}
              onRemove={removeGoal}
            />
          </FormSection>

          {/* <FormSection 
            title="Additional Information" 
            description="Upload documents to help AI make better decisions"
          >
            <p>Upload a PDF file with additional financial or operational information</p>
            <FileUpload 
              file={formData.uploadedFile || null}
              onUpload={handleFileUpload}
              onRemove={handleFileRemove}
            />
          </FormSection> */}

          <div className="form-actions">
            <Button 
              type="default" 
              onClick={() => setCurrentStep(0)}
              style={{ marginRight: '16px' }}
            >
              Back
            </Button>
            <Button 
              type="primary" 
              loading={loading}
              onClick={handleSave}
              style={{ marginRight: '16px', background: '#52c41a', borderColor: '#52c41a' }}
            >
              Save My Inputs
            </Button>
            <Button 
              type="primary" 
              loading={loading}
              onClick={handleGenerateInsights}
            >
              Generate Insights
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default InputForm;