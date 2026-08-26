import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ChatWindow from './components/ChatWindow';
import Sidebar from './components/Sidebar';
import ApprovalModal from './components/ApprovalModal';
import AnalyticsDashboard from './components/AnalyticsDashboard';

const API_BASE = '/api/v1';

export default function App() {
  const [activeTab, setActiveTab] = useState('commerce');
  const [messages, setMessages] = useState([
    {
      sender: 'agent',
      text: '👋 Welcome to Razorpay Agentic Commerce! I am your AI Buyer Agent.\n\nTell me what you are looking for (e.g., "I need ANC wireless headphones under INR 5,000" or "Show developer laptop under INR 70,000").',
      time: new Date().toLocaleTimeString()
    }
  ]);
  const [cart, setCart] = useState({ items: [], total_rupees: 0.0, version: 1 });
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isApprovalOpen, setIsApprovalOpen] = useState(false);
  const [currentCartId, setCurrentCartId] = useState(null);

  // Initial cart creation and audit trail fetch
  useEffect(() => {
    fetch(`${API_BASE}/carts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: 'user_demo_001', merchant_id: 'merchant_demo_001' })
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.cart_id) setCurrentCartId(data.cart_id);
      })
      .catch(() => {});

    fetchAuditLogs();
  }, []);

  const fetchAuditLogs = () => {
    fetch(`${API_BASE}/audit`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) setAuditLogs(data);
      })
      .catch(() => {});
  };

  const fetchCartDetails = (cartId) => {
    if (!cartId) return;
    fetch(`${API_BASE}/carts/${cartId}`)
      .then((res) => res.json())
      .then((data) => {
        setCart(data);
      })
      .catch(() => {});
  };

  const handleSendMessage = async (userText) => {
    const userMsg = { sender: 'user', text: userText, time: new Date().toLocaleTimeString() };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userText,
          session_id: 'demo_session',
          user_id: 'user_demo_001',
          cart_id: currentCartId
        })
      });
      const data = await res.json();

      const agentMsg = {
        sender: 'agent',
        text: data.agent_response || 'Turn completed.',
        time: new Date().toLocaleTimeString()
      };
      setMessages((prev) => [...prev, agentMsg]);

      // Extract cart_id from actions if available
      const lastCartAction = data.actions_taken?.find((a) => a.result?.cart_id);
      const effectiveCartId = data.cart_id || lastCartAction?.result?.cart_id || currentCartId;
      if (effectiveCartId) {
        setCurrentCartId(effectiveCartId);
        fetchCartDetails(effectiveCartId);
      }

      fetchAuditLogs();
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: 'agent', text: '❌ Error connecting to agent server. Ensure FastAPI backend is running on port 8000.', time: new Date().toLocaleTimeString() }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmPayment = async () => {
    if (!currentCartId) return;
    try {
      // 1. Record User Approval
      await fetch(`${API_BASE}/carts/${currentCartId}/approval`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: 'user_demo_001', status: 'APPROVED' })
      });

      // 2. Create Razorpay Test Order
      const orderRes = await fetch(`${API_BASE}/orders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cart_id: currentCartId, user_id: 'user_demo_001' })
      });
      const orderData = await orderRes.json();

      if (orderData.error || orderData.detail) {
        const errorMsg = typeof orderData.detail === 'string' ? orderData.detail : JSON.stringify(orderData.detail || orderData.error);
        throw new Error(errorMsg);
      }

      const completeOrderVerification = async (payId, signature) => {
        const verifyRes = await fetch(`${API_BASE}/payments/verify`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            order_id: orderData.order_id,
            razorpay_payment_id: payId,
            razorpay_signature: signature
          })
        });
        const verifyData = await verifyRes.json();

        setMessages((prev) => [
          ...prev,
          {
            sender: 'agent',
            text: `🎉 **Razorpay Payment Verified & Order Completed!**\nOrder ID: \`${orderData.order_id}\`\nRazorpay Order ID: \`${orderData.razorpay_order_id}\`\nPayment ID: \`${payId}\`\nAmount Paid: INR ${orderData.amount_rupees?.toFixed(2)}`,
            time: new Date().toLocaleTimeString()
          }
        ]);

        // Reset cart to empty — the old cart is now COMPLETED
        setCart({ items: [], total_rupees: 0.0, version: 1 });

        // Create a fresh cart for the next session
        const newCartRes = await fetch(`${API_BASE}/carts`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: 'user_demo_001', merchant_id: 'merchant_demo_001' })
        });
        const newCartData = await newCartRes.json();
        if (newCartData.cart_id) setCurrentCartId(newCartData.cart_id);

        fetchAuditLogs();
      };

      // 3. Launch Razorpay Standard Checkout SDK if available
      if (window.Razorpay && orderData.razorpay_order_id && !orderData.razorpay_order_id.startsWith('order_test_')) {
        const options = {
          key: 'rzp_test_TSF2aLs0qkWNQy',
          amount: Math.round(orderData.amount_rupees * 100),
          currency: orderData.currency || 'INR',
          name: 'Razorpay Agentic Commerce',
          description: 'AI Buyer Authorized Order',
          order_id: orderData.razorpay_order_id,
          handler: function (response) {
            completeOrderVerification(
              response.razorpay_payment_id,
              response.razorpay_signature
            );
          },
          prefill: {
            name: 'Demo AI Buyer',
            email: 'buyer@agentic-commerce.demo',
            contact: '9999999999'
          },
          theme: { color: '#00d2ff' }
        };
        const rzp = new window.Razorpay(options);
        rzp.open();
      } else {
        // Test mode fallback simulation
        const simPayId = `pay_test_${orderData.order_id.slice(-8)}`;
        const simSig = `sig_valid_${orderData.order_id.slice(-8)}`;
        await completeOrderVerification(simPayId, simSig);
      }
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          sender: 'agent',
          text: `❌ **Payment Authorization Blocked**: ${err.message}`,
          time: new Date().toLocaleTimeString()
        }
      ]);
    }
  };

  const handleTriggerFailureDemo = () => {
    handleSendMessage('Trigger test failure demo to show graceful recovery.');
  };

  const handleUpdateItemQty = async (itemId, newQty) => {
    if (!currentCartId) return;
    try {
      await fetch(`${API_BASE}/carts/${currentCartId}/items/${itemId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity: newQty })
      });
      fetchCartDetails(currentCartId);
      fetchAuditLogs();
    } catch (err) {
      console.error('Failed to update cart item qty', err);
    }
  };

  const handleRemoveItem = async (itemId) => {
    if (!currentCartId) return;
    try {
      await fetch(`${API_BASE}/carts/${currentCartId}/items/${itemId}`, {
        method: 'DELETE'
      });
      fetchCartDetails(currentCartId);
      fetchAuditLogs();
    } catch (err) {
      console.error('Failed to remove cart item', err);
    }
  };

  return (
    <div className="app-container">
      <Navbar
        razorpayKeyId="rzp_test_TSF2aLs0qkWNQy"
        policyMaxLimit="1,00,000"
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />
      <main className="main-content">
        {activeTab === 'commerce' ? (
          <>
            <ChatWindow messages={messages} onSendMessage={handleSendMessage} loading={loading} />
            <Sidebar
              cart={cart}
              auditLogs={auditLogs}
              onOpenApproval={() => setIsApprovalOpen(true)}
              onTriggerFailureDemo={handleTriggerFailureDemo}
              onUpdateItemQty={handleUpdateItemQty}
              onRemoveItem={handleRemoveItem}
            />
          </>
        ) : (
          <AnalyticsDashboard />
        )}
      </main>
      <ApprovalModal
        isOpen={isApprovalOpen}
        onClose={() => setIsApprovalOpen(false)}
        cart={cart}
        onConfirmPayment={handleConfirmPayment}
      />
    </div>
  );
}

