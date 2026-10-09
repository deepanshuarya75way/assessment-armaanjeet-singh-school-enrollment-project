'use client';

import React, { useState, useEffect } from 'react';
import { Sparkles, Send, Loader2, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';
import { reportService } from '@/services/reports';

export function AIReportQueryWidget() {
  const [question, setQuestion] = useState('');
  const [targetDate, setTargetDate] = useState(() => 
    new Date().toISOString().split('T')[0]
  );
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState<string | null>(null);
  
 
  const [sessionId, setSessionId] = useState<string>('');

  useEffect(() => {
    setSessionId(crypto.randomUUID());
  }, [targetDate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    try {
      const res = await reportService.askAiQuery({
        session_id: sessionId,
        question: question.trim(),
        target_date: targetDate,
      });
      setAnswer(res.answer);
      setQuestion(''); 
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to get AI insight');
    } finally {
      setLoading(false);
    }
  };

  // 4. Utility to manually flush conversation context locally and on the backend slate
  const handleResetSession = () => {
    setSessionId(crypto.randomUUID());
    setAnswer(null);
    setQuestion('');
    toast.success('Chat memory reset successfully');
  };

  return (
    <div className="rounded-xl border border-indigo-100 bg-gradient-to-r from-indigo-50/70 to-purple-50/70 p-5 shadow-sm space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white shadow-sm">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-gray-900">AI Enrollment Assistant</h3>
            <p className="text-xs text-gray-500">Ask questions about trends and comparison metrics</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {answer && (
            <button
              type="button"
              onClick={handleResetSession}
              className="inline-flex items-center gap-1 rounded-md border border-gray-300 bg-white px-2 py-1 text-xs font-medium text-gray-600 shadow-sm hover:bg-gray-50 hover:text-gray-900 transition-colors"
              title="Reset Chat Memory"
            >
              <RefreshCw className="h-3 w-3" />
              <span>Reset</span>
            </button>
          )}

          <div className="flex items-center gap-2">
            <label className="text-xs text-gray-500 font-medium whitespace-nowrap">Target Date:</label>
            <input
              type="date"
              value={targetDate}
              onChange={(e) => setTargetDate(e.target.value)}
              className="rounded-md border border-gray-300 bg-white px-2.5 py-1 text-xs text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              required
            />
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder={answer ? "Ask a follow-up question..." : "e.g. Which schools showed a decline in enrollment?"}
          className="w-full rounded-lg border border-gray-300 bg-white px-3.5 py-2 text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-sm"
          required
        />
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 disabled:opacity-50 transition-colors whitespace-nowrap"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          <span>{answer ? 'Reply' : 'Ask'}</span>
        </button>
      </form>

      {answer && (
        <div className="rounded-lg border border-indigo-200 bg-white p-4 text-sm text-gray-800 shadow-sm">
          <div className="mb-1 text-xs font-bold uppercase tracking-wider text-indigo-700">Analysis Result</div>
          <div className="prose prose-sm max-w-none whitespace-pre-line text-gray-700 leading-relaxed">
            {answer}
          </div>
        </div>
      )}
    </div>
  );
}
