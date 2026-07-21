"use client";

import React, { useState, useEffect } from "react";
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from "recharts";
import { 
  LayoutDashboard, Tag, HelpCircle, Users, Activity, Search, 
  TrendingUp, AlertTriangle, AlertCircle, CheckCircle, ArrowRight,
  ExternalLink, MessageSquare, ThumbsUp, ChevronDown, ChevronUp, Globe
} from "lucide-react";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("summary");
  const [searchQuery, setSearchQuery] = useState("");
  const [expandedInsight, setExpandedInsight] = useState(null);
  const [expandedTheme, setExpandedTheme] = useState(null);
  const [themeFilter, setThemeFilter] = useState("ALL");
  const [expandedRQ, setExpandedRQ] = useState(null);
  const [triggering, setTriggering] = useState(false);
  const [triggerStatus, setTriggerStatus] = useState("");

  useEffect(() => {
    async function loadData() {
      const rawApiUrl = process.env.NEXT_PUBLIC_API_URL;
      const cleanBaseUrl = rawApiUrl ? rawApiUrl.replace(/\/+$/, "") : "";

      // 1. Attempt API endpoint if NEXT_PUBLIC_API_URL is set
      if (cleanBaseUrl) {
        try {
          const res = await fetch(`${cleanBaseUrl}/api/insights`);
          if (res.ok) {
            const json = await res.json();
            if (json && !json.error) {
              setData(json);
              setLoading(false);
              return;
            }
          }
        } catch (err) {
          console.warn("API endpoint fetch failed, falling back to static insights_export.json:", err);
        }
      }

      // 2. Fallback to bundled static JSON feed in /public/insights_export.json
      try {
        const res = await fetch("/insights_export.json");
        if (!res.ok) {
          throw new Error("Failed to load local insights_export.json");
        }
        const json = await res.json();
        if (json.error) {
          throw new Error(json.error);
        }
        setData(json);
        setLoading(false);
      } catch (err) {
        console.error("Error loading dashboard data:", err);
        setError("Please run the pipeline script (python run_pipeline.py) first to generate data/insights_export.json.");
        setLoading(false);
      }
    }

    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-[#3E0075] border-t-transparent mb-4"></div>
        <p className="text-gray-600 font-semibold">Loading Zepto Discovery Engine...</p>
      </div>
    );
  }

  if (error || !data || data.error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 p-4 text-center">
        <AlertTriangle className="h-16 w-16 text-yellow-500 mb-4" />
        <h2 className="text-xl font-bold text-gray-800 mb-2">Data Feed Offline</h2>
        <p className="text-gray-600 max-w-md mb-6">{error || data?.error || "No data available."}</p>
        <button 
          onClick={() => window.location.reload()} 
          className="zepto-btn-filled"
        >
          Retry Load
        </button>
      </div>
    );
  }

  const { insights, themes, segments, research_questions, source_stats, summary } = data;

  // Filter themes and insights based on search queries
  const filteredInsights = insights.filter(i => 
    i.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    i.finding.toLowerCase().includes(searchQuery.toLowerCase()) ||
    i.root_cause.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredThemes = themes.filter(t => {
    const matchesSearch = t.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.summary.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = themeFilter === "ALL" || t.macro_theme === themeFilter;
    return matchesSearch && matchesFilter;
  });

  // Calculate unique macro themes for filtering
  const macroThemes = ["ALL", ...new Set(themes.map(t => t.macro_theme))];

  // Colors for charts matching Zepto theme
  const CHART_COLORS = ["#3E0075", "#E21A84", "#16A34A", "#F59E0B", "#2563EB", "#7C3AED"];

  // Formatted data for Source Chart
  const sourceChartData = Object.entries(source_stats).map(([key, stat]) => ({
    name: stat.name,
    count: stat.doc_count,
    sentiment: stat.avg_sentiment
  }));

  // Formatted data for Blocked Category breakdown
  const categoryFreq = {};
  themes.forEach(t => {
    t.blocked_categories.forEach(cat => {
      categoryFreq[cat] = (categoryFreq[cat] || 0) + t.doc_count;
    });
  });
  const categoryChartData = Object.entries(categoryFreq).map(([name, value]) => ({
    name,
    value
  })).sort((a,b) => b.value - a.value);

  return (
    <div className="flex flex-col min-h-screen">
      {/* HEADER: Deep Purple Header bar with Magenta border */}
      <header className="zepto-header px-6 py-4 flex flex-wrap items-center justify-between gap-4 sticky top-0 z-40 shadow-md">
        <div className="flex items-center gap-3">
          <div className="bg-white rounded-full p-2 flex items-center justify-center shadow-inner">
            <span className="text-[#3E0075] font-black text-xl tracking-tight">z</span>
          </div>
          <div>
            <h1 className="font-extrabold text-lg tracking-tight text-white m-0">Zepto Discovery Engine</h1>
            <p className="text-xs text-pink-200">AI-Powered Growth Activation Foundation</p>
          </div>
        </div>

        {/* Global Search Bar */}
        <div className="relative w-full max-w-md md:w-80">
          <span className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-4 w-4 text-gray-400" />
          </span>
          <input
            type="text"
            placeholder="Search insights or themes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-purple-950/40 text-white placeholder-purple-200 border border-purple-800 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent text-sm transition"
          />
        </div>
      </header>

      {/* CORE WORKSPACE: Sidebar + Content Layout */}
      <div className="flex flex-1">
        {/* SIDEBAR: Category-style Sticky Navigation */}
        <aside className="w-64 zepto-sidebar flex flex-col shrink-0 border-r">
          <nav className="flex-1 py-4">
            <div 
              onClick={() => setActiveTab("summary")}
              className={`zepto-sidebar-item ${activeTab === "summary" ? "active" : ""}`}
            >
              <LayoutDashboard className="h-5 w-5" />
              <span>Executive Summary</span>
            </div>
            <div 
              onClick={() => setActiveTab("themes")}
              className={`zepto-sidebar-item ${activeTab === "themes" ? "active" : ""}`}
            >
              <Tag className="h-5 w-5" />
              <span>Theme Explorer</span>
            </div>
            <div 
              onClick={() => setActiveTab("research")}
              className={`zepto-sidebar-item ${activeTab === "research" ? "active" : ""}`}
            >
              <HelpCircle className="h-5 w-5" />
              <span>Research Questions</span>
            </div>
            <div 
              onClick={() => setActiveTab("segments")}
              className={`zepto-sidebar-item ${activeTab === "segments" ? "active" : ""}`}
            >
              <Users className="h-5 w-5" />
              <span>User Segments</span>
            </div>
            <div 
              onClick={() => setActiveTab("sources")}
              className={`zepto-sidebar-item ${activeTab === "sources" ? "active" : ""}`}
            >
              <Activity className="h-5 w-5" />
              <span>Source Monitor</span>
            </div>
          </nav>

          <div className="p-4 border-t border-gray-200 bg-gray-50/50 space-y-3">
            <div className="flex items-center gap-2 text-xs text-gray-500 font-semibold uppercase tracking-wider">
              <Globe className="h-3 w-3" />
              <span>System Metadata</span>
            </div>
            <div className="text-xs text-gray-600 space-y-1">
              <p>Analyzed: <strong className="text-gray-800">{summary.total_documents} reviews</strong></p>
              <p>Generated: <strong className="text-gray-800">{new Date(data.generated_at).toLocaleDateString()}</strong></p>
            </div>
            
            {/* Dynamic Pipeline Trigger Button */}
            <div className="pt-2">
              <button
                onClick={() => {
                  const baseApiUrl = process.env.NEXT_PUBLIC_API_URL;
                  if (!baseApiUrl) {
                    setTriggerStatus("API url missing in settings");
                    setTimeout(() => setTriggerStatus(""), 3000);
                    return;
                  }
                  setTriggering(true);
                  setTriggerStatus("Connecting...");
                  fetch(`${baseApiUrl}/api/run-pipeline`, { method: "POST" })
                    .then(res => {
                      if (!res.ok) throw new Error();
                      return res.json();
                    })
                    .then(() => {
                      setTriggerStatus("ETL Started on Railway!");
                      setTriggering(false);
                      setTimeout(() => setTriggerStatus(""), 4000);
                    })
                    .catch(() => {
                      setTriggerStatus("Connection failed");
                      setTriggering(false);
                      setTimeout(() => setTriggerStatus(""), 3000);
                    });
                }}
                disabled={triggering}
                className="w-full bg-[#E21A84] hover:bg-[#FF007F] text-white text-xs font-bold py-2 px-3 rounded-lg flex items-center justify-center gap-2 transition disabled:opacity-50"
              >
                {triggering ? "Starting..." : "Refresh Pipeline Data"}
              </button>
              {triggerStatus && (
                <p className="text-[10px] text-center font-bold text-purple-950 mt-1.5 animate-pulse">
                  {triggerStatus}
                </p>
              )}
            </div>
          </div>
        </aside>

        {/* MAIN DISPLAY WINDOW */}
        <main className="flex-1 p-6 bg-white overflow-y-auto">
          {/* TAB 1: EXECUTIVE SUMMARY */}
          {activeTab === "summary" && (
            <div className="space-y-6">
              {/* Stat Summary Cards row */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="zepto-card flex items-center gap-4">
                  <div className="bg-pink-100 text-[#E21A84] p-3 rounded-full">
                    <MessageSquare className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-black text-[#3E0075]">{summary.total_documents}</h3>
                    <p className="text-xs font-medium text-gray-500 uppercase">Documents Analyzed</p>
                  </div>
                </div>
                <div className="zepto-card flex items-center gap-4">
                  <div className="bg-purple-100 text-[#3E0075] p-3 rounded-full">
                    <Tag className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-black text-[#3E0075]">{summary.total_themes}</h3>
                    <p className="text-xs font-medium text-gray-500 uppercase">Themes Discovered</p>
                  </div>
                </div>
                <div className="zepto-card flex items-center gap-4">
                  <div className="bg-emerald-100 text-[#16A34A] p-3 rounded-full">
                    <TrendingUp className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-black text-[#3E0075]">{summary.total_insights}</h3>
                    <p className="text-xs font-medium text-gray-500 uppercase">Actionable Insights</p>
                  </div>
                </div>
                <div className="zepto-card flex items-center gap-4">
                  <div className="bg-amber-100 text-[#D97706] p-3 rounded-full">
                    <Globe className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-black text-[#3E0075]">{Object.keys(source_stats).length}</h3>
                    <p className="text-xs font-medium text-gray-500 uppercase">Data Sources Active</p>
                  </div>
                </div>
              </div>

              {/* Charts row */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Blocked category chart */}
                <div className="zepto-card lg:col-span-2">
                  <h3 className="text-base font-bold text-gray-800 mb-4 flex items-center gap-2">
                    <AlertCircle className="h-5 w-5 text-[#E21A84]" />
                    <span>Blocked Category Hotspots (Feedback Volume)</span>
                  </h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={categoryChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                        <YAxis tick={{ fontSize: 11 }} />
                        <Tooltip />
                        <Bar dataKey="value" fill="#3E0075" radius={[4, 4, 0, 0]}>
                          {categoryChartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={index === 0 ? "#E21A84" : "#3E0075"} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Source distribution pie */}
                <div className="zepto-card">
                  <h3 className="text-base font-bold text-gray-800 mb-4 flex items-center gap-2">
                    <Activity className="h-5 w-5 text-[#3E0075]" />
                    <span>Source Distribution</span>
                  </h3>
                  <div className="h-64 flex flex-col items-center justify-center">
                    <div className="w-full h-48">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={sourceChartData}
                            cx="50%"
                            cy="50%"
                            innerRadius={50}
                            outerRadius={75}
                            paddingAngle={4}
                            dataKey="count"
                          >
                            {sourceChartData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                    <div className="flex flex-wrap justify-center gap-x-4 gap-y-1 text-xs mt-2">
                      {sourceChartData.map((entry, index) => (
                        <div key={entry.name} className="flex items-center gap-1">
                          <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: CHART_COLORS[index % CHART_COLORS.length] }}></span>
                          <span className="text-gray-600">{entry.name} ({entry.count})</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Insights List Section */}
              <div className="space-y-4">
                <h3 className="text-base font-extrabold text-gray-800 flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-[#3E0075]" />
                  <span>Growth Insights & Experiments</span>
                </h3>
                
                {filteredInsights.length === 0 ? (
                  <div className="text-center py-8 bg-gray-50 rounded-xl border border-dashed text-gray-500">
                    No insights found matching your search.
                  </div>
                ) : (
                  <div className="space-y-4">
                    {filteredInsights.map(insight => {
                      const isExpanded = expandedInsight === insight.id;
                      const level = insight.confidence_level;
                      const badgeClass = level === 'HIGH' ? 'badge-high' : level === 'MEDIUM' ? 'badge-medium' : 'badge-low';
                      
                      return (
                        <div 
                          key={insight.id} 
                          className="border border-gray-200 rounded-xl bg-white shadow-sm overflow-hidden transition-all hover:shadow-md"
                        >
                          {/* Heading summary header */}
                          <div 
                            onClick={() => setExpandedInsight(isExpanded ? null : insight.id)}
                            className="p-5 flex items-center justify-between gap-4 cursor-pointer hover:bg-gray-50 select-none"
                          >
                            <div className="space-y-1">
                              <div className="flex flex-wrap items-center gap-2">
                                <span className={`badge ${badgeClass}`}>{level} CONFIDENCE</span>
                                <span className="text-xs font-semibold text-pink-600 bg-pink-50 px-2 py-0.5 rounded">
                                  {insight.impact.blocked_category}
                                </span>
                              </div>
                              <h4 className="font-extrabold text-gray-900 text-base">{insight.title}</h4>
                            </div>
                            <button className="text-gray-400 hover:text-gray-600">
                              {isExpanded ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
                            </button>
                          </div>
                          
                          {/* Slide down detailed body */}
                          {isExpanded && (
                            <div className="px-5 pb-5 pt-1 border-t border-gray-100 bg-gray-50/50 space-y-4 text-sm">
                              <div>
                                <h5 className="font-bold text-gray-800 uppercase text-xs tracking-wider mb-1">Core Finding</h5>
                                <p className="text-gray-700 leading-relaxed bg-white p-3 rounded-lg border border-gray-200">{insight.finding}</p>
                              </div>
                              <div>
                                <h5 className="font-bold text-gray-800 uppercase text-xs tracking-wider mb-1">Root Cause Analysis</h5>
                                <p className="text-gray-700 leading-relaxed">{insight.root_cause}</p>
                              </div>
                              
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div className="bg-white p-4 rounded-lg border border-gray-200 space-y-2">
                                  <h5 className="font-bold text-gray-800 uppercase text-xs tracking-wider">Impact & Segment</h5>
                                  <p className="text-gray-600">Estimate: <strong className="text-gray-800">{insight.impact.affected_users}</strong></p>
                                  <p className="text-gray-600">Segment: <strong className="text-gray-800">{insight.target_segment.description}</strong></p>
                                  <p className="text-xs text-gray-500 italic mt-1">{insight.target_segment.behavioral_profile}</p>
                                </div>
                                <div className="bg-white p-4 rounded-lg border border-gray-200 space-y-3">
                                  <h5 className="font-bold text-gray-800 uppercase text-xs tracking-wider">Growth Experiment Hypotheses</h5>
                                  {insight.hypotheses.map((h, i) => (
                                    <div key={i} className="border-l-2 border-pink-500 pl-3 py-1 space-y-1">
                                      <p className="text-gray-700 leading-relaxed text-xs"><strong>H{i+1}:</strong> {h.statement}</p>
                                      <div className="flex gap-2 text-[10px] text-gray-500">
                                        <span>Type: <strong className="text-gray-700">{h.experiment_type}</strong></span>
                                        <span>Effort: <strong className="text-gray-700">{h.effort}</strong></span>
                                        <span>Impact: <strong className="text-gray-700">{h.expected_impact}</strong></span>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 2: THEME EXPLORER */}
          {activeTab === "themes" && (
            <div className="space-y-6">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <h3 className="text-base font-extrabold text-gray-800">Cluster Themes Discovered</h3>
                {/* Horizontal Category Pill filters */}
                <div className="flex flex-wrap gap-2">
                  {macroThemes.map(mt => (
                    <button
                      key={mt}
                      onClick={() => setThemeFilter(mt)}
                      className={themeFilter === mt ? "zepto-btn-filled px-3 py-1 text-xs" : "zepto-btn-outline px-3 py-1 text-xs"}
                    >
                      {mt}
                    </button>
                  ))}
                </div>
              </div>

              {filteredThemes.length === 0 ? (
                <div className="text-center py-12 border border-dashed border-gray-200 rounded-xl text-gray-500">
                  No themes match your search/filter criteria.
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {filteredThemes.map(theme => {
                    const isExpanded = expandedTheme === theme.id;
                    const sentClass = theme.avg_sentiment < -0.1 ? "text-red-600" : theme.avg_sentiment > 0.1 ? "text-green-600" : "text-gray-500";
                    
                    return (
                      <div 
                        key={theme.id}
                        className="zepto-card flex flex-col justify-between"
                      >
                        <div className="space-y-2">
                          <div className="flex items-center justify-between gap-2">
                            <span className="text-xs font-bold text-[#3E0075] bg-[#F3EAFF] px-2 py-0.5 rounded">
                              {theme.macro_theme}
                            </span>
                            <span className="text-xs font-semibold text-gray-500">
                              {theme.doc_count} comments
                            </span>
                          </div>
                          <h4 className="font-bold text-gray-900 text-base">{theme.title}</h4>
                          <p className="text-sm text-gray-600">{theme.summary}</p>
                        </div>

                        <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
                          <div className="text-xs text-gray-500">
                            Avg Sentiment: <span className={`font-bold ${sentClass}`}>{theme.avg_sentiment.toFixed(2)}</span>
                          </div>
                          
                          <button
                            onClick={() => setExpandedTheme(isExpanded ? null : theme.id)}
                            className="text-[#E21A84] hover:text-[#FF007F] font-bold text-xs flex items-center gap-1"
                          >
                            <span>{isExpanded ? "Hide Details" : "View Customer Quotes"}</span>
                            <ArrowRight className="h-3 w-3" />
                          </button>
                        </div>

                        {isExpanded && (
                          <div className="mt-4 pt-4 border-t border-gray-100 space-y-4 bg-gray-50/50 p-4 rounded-lg">
                            <h5 className="text-xs font-bold text-gray-800 uppercase tracking-wider mb-2">Sample Quotes</h5>
                            {theme.representative_quotes.map((quote, idx) => (
                              <blockquote key={idx} className="text-xs text-gray-600 italic border-l-2 border-purple-300 pl-3 leading-relaxed">
                                "{quote}"
                              </blockquote>
                            ))}
                            
                            <div className="flex flex-wrap gap-1 mt-2">
                              {theme.blocked_categories.map(c => (
                                <span key={c} className="text-[10px] font-semibold text-[#E21A84] bg-pink-50 border border-pink-100 px-2 py-0.5 rounded">
                                  Blocked: {c}
                                </span>
                              ))}
                              {theme.drivers.map(d => (
                                <span key={d} className="text-[10px] font-semibold text-purple-700 bg-purple-50 border border-purple-100 px-2 py-0.5 rounded">
                                  Driver: {d}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* TAB 3: RESEARCH QUESTIONS */}
          {activeTab === "research" && (
            <div className="space-y-6">
              <h3 className="text-base font-extrabold text-gray-800 mb-2">Strategic Research Questions Mapped</h3>
              <p className="text-sm text-gray-500 mb-4">Click on any card to explore detailed strategic findings, root causes, direct customer evidence, and recommended growth hypotheses.</p>
              <div className="grid grid-cols-1 gap-4">
                {research_questions.map(q => {
                  const badgeClass = q.evidence_strength === 'HIGH' ? 'badge-high' : q.evidence_strength === 'MEDIUM' ? 'badge-medium' : 'badge-low';
                  const isExpanded = expandedRQ === q.id;
                  
                  return (
                    <div 
                      key={q.id} 
                      className="border border-gray-200 rounded-xl bg-white shadow-sm overflow-hidden transition-all hover:shadow-md"
                    >
                      {/* Accordion Toggle Header */}
                      <div 
                        onClick={() => setExpandedRQ(isExpanded ? null : q.id)}
                        className="p-5 flex items-center justify-between gap-4 cursor-pointer hover:bg-gray-50 select-none"
                      >
                        <div className="space-y-2 max-w-3xl">
                          <div className="flex items-center gap-3">
                            <span className="bg-[#3E0075] text-white text-xs font-black px-2.5 py-1 rounded-full">
                              {q.id.split('_')[0].toUpperCase()}
                            </span>
                            <span className={`badge ${badgeClass}`}>{q.evidence_strength} EVIDENCE</span>
                            <span className="text-xs font-semibold text-gray-400">
                              {q.document_count} supporting comments
                            </span>
                          </div>
                          <h4 className="font-extrabold text-gray-950 text-base">{q.question}</h4>
                        </div>
                        
                        <div className="flex items-center gap-3 shrink-0">
                          <button className="text-gray-400 hover:text-gray-600">
                            {isExpanded ? <ChevronUp className="h-5 w-5" /> : <ChevronDown className="h-5 w-5" />}
                          </button>
                        </div>
                      </div>
                      
                      {/* Accordion Expandable Detailed Answers */}
                      {isExpanded && (
                        <div className="px-5 pb-5 pt-2 border-t border-gray-100 bg-gray-50/50 space-y-5 text-sm">
                          {/* Finding Box */}
                          <div className="space-y-2">
                            <h5 className="font-extrabold text-[#3E0075] uppercase text-xs tracking-wider">Direct Strategic Finding</h5>
                            <p className="text-gray-800 leading-relaxed bg-white p-3 rounded-lg border border-gray-200 shadow-sm">
                              {q.finding || "No finding data exported."}
                            </p>
                          </div>
                          
                          {/* Root Cause Box */}
                          <div className="space-y-1">
                            <h5 className="font-extrabold text-gray-800 uppercase text-xs tracking-wider">Root Cause Analysis</h5>
                            <p className="text-gray-700 leading-relaxed">
                              {q.root_cause || "No root cause data exported."}
                            </p>
                          </div>
                          
                          {/* Direct Supporting Quotes */}
                          {q.quotes && q.quotes.length > 0 && (
                            <div className="space-y-2">
                              <h5 className="font-extrabold text-gray-800 uppercase text-xs tracking-wider flex items-center gap-1.5">
                                <MessageSquare className="h-4 w-4 text-[#E21A84]" />
                                <span>Verbatim Customer Evidence</span>
                              </h5>
                              <div className="space-y-2">
                                {q.quotes.map((quote, idx) => (
                                  <blockquote 
                                    key={idx} 
                                    className="text-xs text-gray-600 italic border-l-2 border-pink-400 pl-3 leading-relaxed bg-white/40 p-2 rounded-r-lg"
                                  >
                                    "{quote}"
                                  </blockquote>
                                ))}
                              </div>
                            </div>
                          )}
                          
                          {/* Growth Hypothesis Promotion Card */}
                          {q.hypothesis && q.hypothesis.statement && (
                            <div className="bg-[#F3EAFF] border border-[#E5D5FF] p-4 rounded-xl space-y-3">
                              <h5 className="font-extrabold text-[#3E0075] uppercase text-xs tracking-wider flex items-center gap-1.5">
                                <TrendingUp className="h-4 w-4" />
                                <span>Recommended Growth Experiment</span>
                              </h5>
                              <p className="text-gray-900 font-medium text-xs leading-relaxed">
                                <strong>Hypothesis:</strong> {q.hypothesis.statement}
                              </p>
                              <div className="flex flex-wrap gap-4 text-[10px] text-purple-900 font-bold bg-white/80 py-1.5 px-3 rounded-lg w-fit">
                                <span>Experiment Type: <strong className="text-purple-700">{q.hypothesis.type}</strong></span>
                                <span className="text-purple-300">|</span>
                                <span>Effort Level: <strong className="text-purple-700">{q.hypothesis.effort}</strong></span>
                                <span className="text-purple-300">|</span>
                                <span>Expected Impact: <strong className="text-purple-700">{q.hypothesis.impact}</strong></span>
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* TAB 4: USER SEGMENTS */}
          {activeTab === "segments" && (
            <div className="space-y-6">
              <h3 className="text-base font-extrabold text-gray-800">Growth Segment Profiles</h3>
              <div className="grid grid-cols-1 gap-6">
                {segments.map(segment => {
                  const potential = segment.cross_category_potential;
                  const barWidth = potential === 'Very High' ? 'w-full bg-[#E21A84]' : potential === 'High' ? 'w-4/5 bg-[#E21A84]' : potential === 'Medium' ? 'w-3/5 bg-[#3E0075]' : 'w-2/5 bg-gray-400';
                  
                  return (
                    <div key={segment.id} className="zepto-card grid grid-cols-1 md:grid-cols-3 gap-6">
                      <div className="space-y-2">
                        <h4 className="font-extrabold text-[#3E0075] text-lg">{segment.name}</h4>
                        <p className="text-2xl font-black text-gray-800">{segment.estimated_size}</p>
                        <p className="text-xs uppercase font-bold text-gray-400 tracking-wider">Estimated Segment Size</p>
                      </div>
                      
                      <div className="space-y-2 border-t md:border-t-0 md:border-l md:border-r border-gray-200 pt-4 md:pt-0 md:px-6">
                        <h5 className="text-xs font-bold text-gray-800 uppercase tracking-wider">Behavioral Profile</h5>
                        <p className="text-sm text-gray-600 leading-relaxed">{segment.description}</p>
                        <p className="text-xs text-gray-500 italic mt-1">{segment.behavioral_profile}</p>
                      </div>
                      
                      <div className="space-y-3 pt-4 md:pt-0">
                        <div className="space-y-1">
                          <span className="text-xs font-bold text-gray-800 uppercase tracking-wider block">Cross-Category Potential: {potential}</span>
                          <div className="w-full bg-gray-200 h-2 rounded-full overflow-hidden">
                            <div className={`h-full ${barWidth}`}></div>
                          </div>
                        </div>
                        <div className="space-y-1">
                          <span className="text-xs font-bold text-[#E21A84] uppercase tracking-wider block">Growth Intervention</span>
                          <p className="text-xs text-gray-700 font-medium leading-relaxed bg-pink-50 border border-pink-100 p-2 rounded-lg">
                            {segment.recommended_intervention}
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* TAB 5: SOURCE MONITOR */}
          {activeTab === "sources" && (
            <div className="space-y-6">
              <h3 className="text-base font-extrabold text-gray-800">Source Platform Metrics</h3>
              
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Volume bar chart */}
                <div className="zepto-card lg:col-span-2">
                  <h4 className="font-bold text-gray-800 text-sm mb-4">Volume per Platform</h4>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={sourceChartData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count" fill="#3E0075" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
                
                {/* Sentiment comparison chart */}
                <div className="zepto-card">
                  <h4 className="font-bold text-gray-800 text-sm mb-4">Average Sentiment by Platform</h4>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={sourceChartData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                        <YAxis domain={[-1, 1]} />
                        <Tooltip />
                        <Bar dataKey="sentiment" fill="#E21A84" radius={[4, 4, 0, 0]}>
                          {sourceChartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.sentiment >= 0 ? "#16A34A" : "#DC2626"} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>

              {/* Data Sources table */}
              <div className="zepto-card overflow-hidden">
                <h4 className="font-bold text-gray-800 text-sm mb-4">Active Connectors Summary</h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-sm">
                    <thead>
                      <tr className="border-b border-gray-200 text-gray-500 font-bold">
                        <th className="pb-3">Connector Source</th>
                        <th className="pb-3">Unique Docs Ingested</th>
                        <th className="pb-3">Avg Words/Doc</th>
                        <th className="pb-3">Avg Rating (Play Store)</th>
                        <th className="pb-3 text-right">Avg Sentiment Score</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100 font-medium">
                      {Object.entries(source_stats).map(([key, stat]) => (
                        <tr key={key} className="hover:bg-gray-50">
                          <td className="py-3 text-gray-900 font-bold">{stat.name}</td>
                          <td className="py-3 text-gray-600">{stat.doc_count}</td>
                          <td className="py-3 text-gray-600">{stat.avg_words} words</td>
                          <td className="py-3 text-gray-600">{stat.avg_rating ? `${stat.avg_rating} / 5.0` : "N/A"}</td>
                          <td className={`py-3 text-right ${stat.avg_sentiment >= 0 ? "text-green-600" : "text-red-600"}`}>
                            {stat.avg_sentiment.toFixed(3)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
