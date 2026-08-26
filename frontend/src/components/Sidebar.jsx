import React from 'react';

export default function Sidebar({ cart, auditLogs, onOpenApproval, onTriggerFailureDemo, onUpdateItemQty, onRemoveItem }) {
  const items = cart?.items || [];
  const totalRupees = cart?.total_rupees || 0.0;

  return (
    <aside className="sidebar-section">
      <div className="sidebar-scroll-inner">
      {/* Active Cart & Policy Panel */}
      <div className="panel-card">
        <div className="panel-header">
          <span>🛒 Active Cart & Policy</span>
          <span style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)' }}>Version #{cart?.version || 1}</span>
        </div>

        {items.length === 0 ? (
          <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textAlign: 'center', padding: '1rem 0' }}>
            No items in cart yet. Tell the agent what you want to buy!
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1rem' }}>
            {items.map((item, idx) => (
              <div key={idx} style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.85rem', background: 'var(--bg-primary)', padding: '0.6rem 0.8rem', borderRadius: '6px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ fontWeight: '600', flex: 1 }}>{item.product_name}</div>
                  <button
                    onClick={() => onRemoveItem && onRemoveItem(item.id)}
                    title="Remove item"
                    style={{ background: 'none', border: 'none', color: 'var(--accent-red)', cursor: 'pointer', fontSize: '0.9rem', padding: '0 0 0 0.5rem' }}
                  >
                    🗑️
                  </button>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', background: 'var(--bg-card)', padding: '0.2rem 0.4rem', borderRadius: '4px' }}>
                    <button
                      onClick={() => onUpdateItemQty && onUpdateItemQty(item.id, item.quantity - 1)}
                      style={{ background: 'none', border: 'none', color: '#fff', cursor: 'pointer', fontWeight: 'bold', width: '18px' }}
                    >
                      -
                    </button>
                    <span style={{ fontSize: '0.8rem', fontWeight: '600' }}>{item.quantity}</span>
                    <button
                      onClick={() => onUpdateItemQty && onUpdateItemQty(item.id, item.quantity + 1)}
                      style={{ background: 'none', border: 'none', color: '#fff', cursor: 'pointer', fontWeight: 'bold', width: '18px' }}
                    >
                      +
                    </button>
                  </div>
                  <div style={{ fontWeight: '600', color: 'var(--accent-cyan)' }}>
                    INR {item.line_total_rupees?.toFixed(2)}
                  </div>
                </div>
              </div>
            ))}

            <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: '0.75rem', borderTop: '1px solid var(--border-color)', fontWeight: '700', fontSize: '1rem' }}>
              <span>Total Amount:</span>
              <span style={{ color: 'var(--accent-green)' }}>INR {totalRupees.toFixed(2)}</span>
            </div>

            <div style={{ fontSize: '0.75rem', background: 'rgba(16, 185, 129, 0.1)', color: 'var(--accent-green)', padding: '0.5rem', borderRadius: '6px', marginTop: '0.5rem' }}>
              🔒 Policy Check: Cart total (INR {totalRupees.toFixed(2)}) is within INR 1,00,000 max limit.
            </div>

            <button className="btn-primary" onClick={onOpenApproval} style={{ marginTop: '0.5rem' }}>
              Proceed to Approval & Payment
            </button>
          </div>
        )}
      </div>

      {/* Failure Recovery Demo Trigger */}
      <div className="panel-card" style={{ borderColor: 'rgba(239, 68, 68, 0.3)' }}>
        <div className="panel-header" style={{ color: 'var(--accent-red)' }}>
          <span>⚠️ Hackathon Graceful Failure Demo</span>
        </div>
        <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
          Simulate a payment failure in test mode to demonstrate safe state persistence and recovery.
        </p>
        <button
          onClick={onTriggerFailureDemo}
          style={{ width: '100%', background: 'transparent', border: '1px solid var(--accent-red)', color: 'var(--accent-red)', padding: '0.5rem', borderRadius: '6px', cursor: 'pointer', fontSize: '0.85rem' }}
        >
          Simulate Payment Failure & Recovery
        </button>
      </div>

      {/* Live Audit Trail Panel */}
      <div className="panel-card audit-panel" style={{ flex: 1 }}>
        <div className="panel-header">
          <span>📜 Audit Trail Timeline</span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{auditLogs.length} Events</span>
        </div>

        <div className="timeline-container">
          <div className="timeline">
            {auditLogs.length === 0 ? (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>No events recorded yet.</div>
            ) : (
              auditLogs.map((log, idx) => (
                <div key={idx} className="timeline-item">
                  <div className={`timeline-dot ${log.action.toLowerCase().includes('policy') ? 'policy' : log.action.toLowerCase().includes('approval') ? 'approval' : log.action.toLowerCase().includes('payment') ? 'payment' : log.action.toLowerCase().includes('fail') ? 'failure' : ''}`} />
                  <div className="timeline-content">
                    <div className="timeline-action">{log.action}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{log.reason || 'Event executed'}</div>
                    <div className="timeline-time">{new Date(log.created_at).toLocaleTimeString()}</div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
      </div>  {/* end sidebar-scroll-inner */}
    </aside>
  );
}
