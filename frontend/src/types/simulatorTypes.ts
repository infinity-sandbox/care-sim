export interface RevenueSource {
  id: string;
  sourceName: string;
  monthlyAmount: number | null; // Changed to allow null;
  tag: string;
}

export interface ExpenseItem {
  id: string;
  expenseName: string;
  monthlyAmount: number | null;
  hoursPerMonth?: number | null;
  type: string;
}

// Create a specific interface for employee expenses
export interface EmployeeExpense extends ExpenseItem {
  hoursPerMonth: number | null;
}

export interface Classroom {
  id: string;
  name: string;
  capacity: number | null;
  ratio: number | null;
  avgStudents: number | null;
}

export interface BusinessGoal {
  id: string;
  goal: string;
  targetPercentage: number | null;
}

export interface FormData {
  businessName: string;
  revenueSources: RevenueSource[];
  employees: ExpenseItem[];
  facilities: ExpenseItem[];
  administrative: ExpenseItem[];
  supplies: ExpenseItem[];
  classrooms: Classroom[];
  operatingHours: number | null;
  operatingDays: number | null;
  goals: BusinessGoal[];
  uploadedFile?: File | null;
}

export interface InsightData {
  net_monthly_income: {
    value: number;
    currency: string;
    calculation: string;
    note: string;
  };
  break_even_enrollment: {
    value: number;
    unit: string;
    calculation: string;
    note: string;
  };
  largest_expense: {
    category: string;
    percentage_of_total_expenses: number;
    calculation: string;
  };
  capacity_utilization: {
    value: number;
    unit: string;
    calculation: string;
    note: string;
  };
  executive_summary: {
    financial_overview: string;
    profitability_status: string;
    enrollment_status: string;
    recommendations: string[];
  };
}

export interface Recommendations {
  recommendations: string[];
}

// Add Recommendations interface
export interface Recommendations {
  recommendations: string[];
}