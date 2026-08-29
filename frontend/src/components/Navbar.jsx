import React from 'react';

export default function Navbar({ razorpayKeyId, policyMaxLimit, activeTab, setActiveTab }) {
  return (
    <header className="navbar">
      <div className="brand-section">
        <div className="brand-logo">
          <span>⚡ Razorpay</span>
          <span style={{ color: 'var(--accent-cyan)' }}>Agentic Commerce</span>
        </div>
        <span className="brand-badge">Track 01</span>
      </div>

      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
        <button
          onClick={() => setActiveTab('commerce')}
          style={{
            background: activeTab === 'commerce' ? 'var(--accent-cyan)' : 'transparent',
            color: activeTab === 'commerce' ? '#000' : 'var(--text-secondary)',
            border: '1px solid var(--border-color)',
            padding: '0.45rem 0.9rem',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '0.85rem'
          }}
        >
          🤖 AI Commerce Agent
        </button>
        <button
          onClick={() => setActiveTab('analytics')}
          style={{
            background: activeTab === 'analytics' ? 'var(--accent-cyan)' : 'transparent',
            color: activeTab === 'analytics' ? '#000' : 'var(--text-secondary)',
            border: '1px solid var(--border-color)',
            padding: '0.45rem 0.9rem',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '0.85rem'
          }}
        >
          📈 Merchant Growth Telemetry
        </button>
        <button
          onClick={() => setActiveTab('admin')}
          style={{
            background: activeTab === 'admin' ? 'var(--accent-cyan)' : 'transparent',
            color: activeTab === 'admin' ? '#000' : 'var(--text-secondary)',
            border: '1px solid var(--border-color)',
            padding: '0.45rem 0.9rem',
            borderRadius: '6px',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '0.85rem'
          }}
        >
          ⚙️ Merchant Admin
        </button>
      </div>

      <div className="nav-metrics">
        <div className="metric-pill">
          <span>Key ID:</span>
          <strong>
            {razorpayKeyId && razorpayKeyId.length > 14
              ? `${razorpayKeyId.slice(0, 14)}...`
              : razorpayKeyId || 'rzp_test_...'}
          </strong>
        </div>
        <div className="metric-pill">
          <span>Policy Cap:</span>
          <strong style={{ color: 'var(--accent-amber)' }}>INR {policyMaxLimit || '1,00,000'}</strong>
        </div>
        <div className="metric-pill" style={{ borderColor: 'var(--accent-green)' }}>
          <span style={{ color: 'var(--accent-green)' }}>● Engine Online</span>
        </div>
      </div>
    </header>
  );
}
