"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@clerk/nextjs";
import { useRouter } from "next/navigation";
import api, { Strategy, Business } from "@/lib/api";

export default function StrategiesPage() {
  const { getToken } = useAuth();
  const router = useRouter();
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [selectedBusiness, setSelectedBusiness] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const token = await getToken();
      if (!token) {
        router.push("/sign-in");
        return;
      }

      // Load businesses and strategies
      const [businessesData, strategiesData] = await Promise.all([
        api.businesses.list(token),
        api.strategies.list(undefined, token),
      ]);

      setBusinesses(businessesData);
      setStrategies(strategiesData);
      
      // Select first business by default
      if (businessesData.length > 0 && !selectedBusiness) {
        setSelectedBusiness(businessesData[0].id);
      }
    } catch (err: any) {
      setError(err.message || "Failed to load data");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateStrategy = async () => {
    if (!selectedBusiness) {
      setError("Please select a business first");
      return;
    }

    setGenerating(true);
    setError("");

    try {
      const token = await getToken();
      if (!token) {
        router.push("/sign-in");
        return;
      }

      const newStrategy = await api.strategies.generate(
        { business_id: selectedBusiness },
        token
      );

      setStrategies([newStrategy, ...strategies]);
      setError("");
    } catch (err: any) {
      setError(err.message || "Failed to generate strategy");
    } finally {
      setGenerating(false);
    }
  };

  const filteredStrategies = selectedBusiness
    ? strategies.filter((s) => s.business_id === selectedBusiness)
    : strategies;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading strategies...</p>
        </div>
      </div>
    );
  }

  if (businesses.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
          <h2 className="text-xl font-semibold text-yellow-900 mb-2">
            No Business Found
          </h2>
          <p className="text-yellow-700 mb-4">
            You need to set up a business first before generating strategies.
          </p>
          <button
            onClick={() => router.push("/onboarding")}
            className="bg-yellow-600 text-white px-6 py-2 rounded-lg hover:bg-yellow-700 transition"
          >
            Set Up Business
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Marketing Strategies
        </h1>
        <p className="text-gray-600">
          AI-powered marketing strategies tailored to your business
        </p>
      </div>

      {/* Business Selector & Generate Button */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Business
            </label>
            <select
              value={selectedBusiness || ""}
              onChange={(e) => setSelectedBusiness(Number(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {businesses.map((business) => (
                <option key={business.id} value={business.id}>
                  {business.name}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleGenerateStrategy}
            disabled={generating || !selectedBusiness}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 mt-6 sm:mt-0"
          >
            {generating ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Generating...
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Generate Strategy
              </>
            )}
          </button>
        </div>

        {error && (
          <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-700">{error}</p>
          </div>
        )}
      </div>

      {/* Strategies List */}
      {filteredStrategies.length === 0 ? (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-12 text-center">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-gray-900">No strategies yet</h3>
          <p className="mt-2 text-gray-600">
            Generate your first AI-powered marketing strategy using the button above.
          </p>
        </div>
      ) : (
        <div className="grid gap-6">
          {filteredStrategies.map((strategy) => (
            <div
              key={strategy.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition cursor-pointer"
              onClick={() => router.push(`/strategies/${strategy.id}`)}
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {strategy.title}
                  </h3>
                  {strategy.description && (
                    <p className="text-gray-600">{strategy.description}</p>
                  )}
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  strategy.status === 'active' ? 'bg-green-100 text-green-800' :
                  strategy.status === 'draft' ? 'bg-gray-100 text-gray-800' :
                  'bg-blue-100 text-blue-800'
                }`}>
                  {strategy.status}
                </span>
              </div>

              <div className="text-sm text-gray-500">
                Created {new Date(strategy.created_at).toLocaleDateString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
