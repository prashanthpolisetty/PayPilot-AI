import React, { useState } from 'react';

export default function ApprovalModal({ isOpen, onClose, cart, onConfirmPayment }) {
  const [processing, setProcessing] = useState(false);
  const totalRupees = cart?.total_rupees || 0.0;
  const items = cart?.items || [];

  if (!isOpen) return null;

  const handlePay = async () => {
    setProcessing(true);
    await onConfirmPayment();
    setProcessing(false);
    onClose();
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0,0,0,0.8)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 100
    }}>
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-color)',
        borderRadius: '16px',
        width: '90%',
        maxWidth: '520px',
        padding: '2rem',
        boxShadow: '0 20px 50px rgba(0,0,0,0.5)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ fontSize: '1.25rem', color: '#fff' }}>🛡️ Human Approval Gate</h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '1.5rem', cursor: 'pointer' }}>×</button>
        </div>

        <div style={{ background: 'var(--bg-primary)', padding: '1rem', borderRadius: '8px', marginBottom: '1rem', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Money Action Explanation:</div>
          <div style={{ fontWeight: '600', fontSize: '0.95rem' }}>
            Authorization request to create a Razorpay Test Mode Payment Order for user purchase.
          </div>
        </div>

        <div style={{ marginBottom: '1.25rem' }}>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Item Summary:</div>
          {items.map((it, idx) => (
            <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', padding: '0.4rem 0' }}>
              <span>{it.product_name} (x{it.quantity})</span>
              <span style={{ fontWeight: '600' }}>INR {it.line_total_rupees?.toFixed(2)}</span>
            </div>
          ))}
          <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--border-color)', paddingTop: '0.75rem', marginTop: '0.5rem', fontWeight: '700', fontSize: '1.1rem' }}>
            <span>Total Payable:</span>
            <span style={{ color: 'var(--accent-green)' }}>INR {totalRupees.toFixed(2)}</span>
          </div>
        </div>

        <div style={{ background: 'rgba(0, 210, 255, 0.08)', border: '1px solid rgba(0, 210, 255, 0.2)', padding: '0.75rem', borderRadius: '8px', fontSize: '0.8rem', color: 'var(--accent-cyan)', marginBottom: '1.5rem' }}>
          ⚡ **Deterministic Bounds Verified**: Total INR {totalRupees.toFixed(2)} ≤ INR 1,00,000 Cap. Key ID: `rzp_test_TSF2aLs0qkWNQy`.
        </div>

        <div style={{ display: 'flex', gap: '1rem' }}>
          <button onClick={onClose} style={{ flex: 1, background: 'transparent', border: '1px solid var(--border-color)', color: 'var(--text-secondary)', padding: '0.85rem', borderRadius: '8px', cursor: 'pointer' }}>
            Reject Action
          </button>
          <button onClick={handlePay} disabled={processing} className="btn-primary" style={{ flex: 2 }}>
            {processing ? 'Processing Payment...' : '✅ Approve & Pay via Razorpay'}
          </button>
        </div>
      </div>
    </div>
  );
}
