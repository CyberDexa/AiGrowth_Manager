"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@clerk/nextjs";
import { useRouter, useParams } from "next/navigation";
import api, { Strategy } from "@/lib/api";
import ReactMarkdown from 'react-markdown';

export default function StrategyDetailPage() {
  const { getToken } = useAuth();
  const router = useRouter();
  const params = useParams();
  const strategyId = params.id as string;

  const [strategy, setStrategy] = useState<Strategy | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    loadStrategy();
  }, [strategyId]);

  const loadStrategy = async () => {
    try {
      const token = await getToken();
      if (!token) {
        router.push("/sign-in");
        return;
      }

      const data = await api.strategies.get(Number(strategyId), token);
      setStrategy(data);
    } catch (err: any) {
      setError(err.message || "Failed to load strategy");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading strategy...</p>
        </div>
      </div>
    );
  }

  if (error || !strategy) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-700">{error || "Strategy not found"}</p>
          <button
            onClick={() => router.push("/strategies")}
            className="mt-4 text-blue-600 hover:underline"
          >
            Back to Strategies
          </button>
        </div>
      </div>
    );
  }

  const sections = [
    { key: "executive_summary", label: "Executive Summary", icon: "📋" },
    { key: "market_analysis", label: "Market Analysis", icon: "📊" },
    { key: "objectives", label: "Objectives", icon: "🎯" },
    { key: "channel_strategy", label: "Channel Strategy", icon: "📢" },
    { key: "content_pillars", label: "Content Pillars", icon: "📝" },
    { key: "tactics", label: "Key Tactics", icon: "⚡" },
    { key: "metrics", label: "Success Metrics", icon: "📈" },
    { key: "budget", label: "Budget", icon: "💰" },
    { key: "timeline", label: "Timeline", icon: "📅" },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => router.push("/strategies")}
          className="text-blue-600 hover:underline mb-4 flex items-center gap-2"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Strategies
        </button>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {strategy.title}
            </h1>
            {strategy.description && (
              <p className="text-gray-600">{strategy.description}</p>
            )}
            <p className="text-sm text-gray-500 mt-2">
              Created {new Date(strategy.created_at).toLocaleDateString()}
            </p>
          </div>
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            strategy.status === 'active' ? 'bg-green-100 text-green-800' :
            strategy.status === 'draft' ? 'bg-gray-100 text-gray-800' :
            'bg-blue-100 text-blue-800'
          }`}>
            {strategy.status}
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex gap-4 overflow-x-auto">
          <button
            onClick={() => setActiveTab("overview")}
            className={`py-3 px-4 border-b-2 font-medium text-sm whitespace-nowrap ${
              activeTab === "overview"
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Full Strategy
          </button>
          {sections.map((section) => (
            strategy.strategy_data[section.key as keyof typeof strategy.strategy_data] && (
              <button
                key={section.key}
                onClick={() => setActiveTab(section.key)}
                className={`py-3 px-4 border-b-2 font-medium text-sm whitespace-nowrap ${
                  activeTab === section.key
                    ? "border-blue-600 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                {section.icon} {section.label}
              </button>
            )
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        {activeTab === "overview" ? (
          <div className="prose max-w-none">
            <ReactMarkdown>
              {strategy.strategy_data.full_text || "No strategy content available"}
            </ReactMarkdown>
          </div>
        ) : (
          <div className="prose max-w-none">
            <ReactMarkdown>
              {strategy.strategy_data[activeTab as keyof typeof strategy.strategy_data] as string || "No content available for this section"}
            </ReactMarkdown>
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="mt-6 flex gap-4">
        <button
          onClick={() => {
            // TODO: Implement export functionality
            alert("Export feature coming soon!");
          }}
          className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
        >
          Export as PDF
        </button>
        <button
          onClick={() => {
            // TODO: Implement share functionality
            alert("Share feature coming soon!");
          }}
          className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
        >
          Share Strategy
        </button>
      </div>
    </div>
  );
}
