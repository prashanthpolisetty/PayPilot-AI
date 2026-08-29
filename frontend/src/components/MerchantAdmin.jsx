import React, { useState, useEffect } from 'react';

export default function MerchantAdmin() {
  const merchantId = 'merchant_demo_001';
  const [config, setConfig] = useState({
    max_transaction_limit_rupees: 100000,
    max_daily_spend_rupees: 200000,
    max_quantity_per_item: 5,
    risk_scoring_enabled: true
  });
  const [coupons, setCoupons] = useState([]);
  const [newCoupon, setNewCoupon] = useState({ code: '', discount_value: 10, min_cart_rupees: 1000 });
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchConfig();
    fetchCoupons();
  }, []);

  const fetchConfig = () => {
    fetch(`/api/v1/merchant/config/${merchantId}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.merchant_id) setConfig(data);
      })
      .catch(() => {});
  };

  const fetchCoupons = () => {
    fetch(`/api/v1/merchant/coupons/${merchantId}`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) setCoupons(data);
      })
      .catch(() => {});
  };

  const handleSaveConfig = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch(`/api/v1/merchant/config/${merchantId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      const data = await res.json();
      setMessage('✅ Policy Configuration Saved Successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      setMessage('❌ Failed to save configuration');
    }
  };

  const handleCreateCoupon = async (e) => {
    e.preventDefault();
    if (!newCoupon.code) return;
    try {
      await fetch(`/api/v1/merchant/coupons`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...newCoupon, merchant_id: merchantId })
      });
      setNewCoupon({ code: '', discount_value: 10, min_cart_rupees: 1000 });
      fetchCoupons();
      setMessage('🎉 Promotional Coupon Created!');
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      setMessage('❌ Failed to create coupon');
    }
  };

  return (
    <div style={{ padding: '1.5rem', width: '100%', overflowY: 'auto', color: '#fff' }}>
      <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: '700', marginBottom: '0.25rem' }}>
            ⚙️ Merchant Governance & Policy Control
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Configure merchant-side transaction caps, risk scoring thresholds, and active AI promotion codes.
          </p>
        </div>
        {message && <div className="brand-badge" style={{ background: 'var(--accent-green)', color: '#000' }}>{message}</div>}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.5rem' }}>
        {/* Dynamic Policy Config Card */}
        <div className="panel-card" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', color: 'var(--accent-cyan)' }}>
            🛡️ Bounded Policy Engine Limits
          </h3>
          <form onSubmit={handleSaveConfig}>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                Max Transaction Limit (Paise / INR)
              </label>
              <input
                type="number"
                value={config.max_transaction_limit_rupees}
                onChange={(e) => setConfig({ ...config, max_transaction_limit_rupees: parseFloat(e.target.value) })}
                style={{ width: '100%', padding: '0.6rem', borderRadius: '6px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: '#fff' }}
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                Max Daily Spend Cap per User (INR)
              </label>
              <input
                type="number"
                value={config.max_daily_spend_rupees}
                onChange={(e) => setConfig({ ...config, max_daily_spend_rupees: parseFloat(e.target.value) })}
                style={{ width: '100%', padding: '0.6rem', borderRadius: '6px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: '#fff' }}
              />
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.3rem' }}>
                Max Quantity per Cart Line Item
              </label>
              <input
                type="number"
                value={config.max_quantity_per_item}
                onChange={(e) => setConfig({ ...config, max_quantity_per_item: parseInt(e.target.value) })}
                style={{ width: '100%', padding: '0.6rem', borderRadius: '6px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: '#fff' }}
              />
            </div>

            <div style={{ marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <input
                type="checkbox"
                id="risk-toggle"
                checked={config.risk_scoring_enabled}
                onChange={(e) => setConfig({ ...config, risk_scoring_enabled: e.target.checked })}
              />
              <label htmlFor="risk-toggle" style={{ fontSize: '0.85rem', color: '#fff' }}>
                Enable AI Risk Scoring Engine (Block Anomaly Carts)
              </label>
            </div>

            <button type="submit" className="brand-badge" style={{ width: '100%', padding: '0.75rem', border: 'none', cursor: 'pointer', fontWeight: '700', fontSize: '0.9rem' }}>
              Save Policy Controls
            </button>
          </form>
        </div>

        {/* AI Coupon Management Card */}
        <div className="panel-card" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', color: 'var(--accent-amber)' }}>
            🏷️ Promotional Coupon Codes
          </h3>
          <form onSubmit={handleCreateCoupon} style={{ marginBottom: '1.25rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', marginBottom: '0.75rem' }}>
              <input
                type="text"
                placeholder="Coupon Code (e.g. SAVE10)"
                value={newCoupon.code}
                onChange={(e) => setNewCoupon({ ...newCoupon, code: e.target.value })}
                style={{ padding: '0.6rem', borderRadius: '6px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: '#fff' }}
              />
              <input
                type="number"
                placeholder="Discount %"
                value={newCoupon.discount_value}
                onChange={(e) => setNewCoupon({ ...newCoupon, discount_value: parseFloat(e.target.value) })}
                style={{ padding: '0.6rem', borderRadius: '6px', background: 'var(--bg-primary)', border: '1px solid var(--border-color)', color: '#fff' }}
              />
            </div>
            <button type="submit" className="brand-badge" style={{ width: '100%', padding: '0.6rem', border: 'none', cursor: 'pointer', background: 'var(--accent-amber)', color: '#000', fontWeight: '700' }}>
              + Create Coupon Code
            </button>
          </form>

          <div style={{ fontSize: '0.85rem', fontWeight: '700', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
            Active Coupons ({coupons.length})
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxHeight: '200px', overflowY: 'auto' }}>
            {coupons.length === 0 ? (
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>No coupons created yet.</div>
            ) : (
              coupons.map((c) => (
                <div key={c.id} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem 0.75rem', background: 'var(--bg-primary)', borderRadius: '6px', border: '1px solid var(--border-color)', fontSize: '0.85rem' }}>
                  <span style={{ fontWeight: '700', color: 'var(--accent-cyan)' }}>{c.code}</span>
                  <span style={{ color: 'var(--accent-green)' }}>{c.discount_value}% OFF</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
