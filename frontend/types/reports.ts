export type CategoryEnum = 'SC' | 'ST' | 'OBC' | 'BC' | 'GENERAL';

export interface ReportDataResponse {
  id: number;
  school_id: number;
  school_name?: string | null;
  class_?: number | string;
  class?: number | string;
  category: CategoryEnum | null;
  boys: number;
  girls: number;
  below_6?: number;
  between_6_and_11?: number;
  above_11?: number;
}

export interface ReportResponse {
  id: number;
  report_month: string; 
  generated_at: string; // ISO datetime string
  status: string;
}

export interface ReportDetailResponse extends ReportResponse {
  data: ReportDataResponse[];
}

export interface AIQueryRequest {
  session_id : string,
  question: string;
  target_date: string; // ISO date format: YYYY-MM-DD
}

export interface AIQueryResponse {
  answer: string;
}