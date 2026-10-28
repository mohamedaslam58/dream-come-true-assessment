import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';

type Tx = { id: number; amount: string; kind: string; status: string; reference: string; failure_reason: string | null };
const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

function App() {
  const [userId, setUserId] = useState<string>('1');
  const [items, setItems] = useState<Tx[]>([]);
  const [error, setError] = useState<string>('');
  const [selected, setSelected] = useState<Tx | null>(null);
  const [balance, setBalance] = useState<string>('0.00');

  const fetchWalletData = () => {
    setError('');
    // Fetch Wallet Balance
    fetch(`${API}/wallet`, { headers: { 'X-User-Id': userId } })
      .then(r => {
        if (!r.ok) throw new Error('Failed to load wallet');
        return r.json();
      })
      .then(data => setBalance(data.balance))
      .catch(() => setError('Unable to load wallet data'));

    // Fetch Transactions with Tenant Header
    fetch(`${API}/transactions`, { headers: { 'X-User-Id': userId } })
      .then(r => {
        if (!r.ok) throw new Error('Failed to load transactions');
        return r.json();
      })
      .then(setItems)
      .catch(() => setError('Unable to load transactions'));
  };

  useEffect(() => {
    fetchWalletData();
  }, [userId]);

  return (
    <main style={{ maxWidth: 850, margin: '40px auto', fontFamily: 'sans-serif', padding: '0 20px' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h1>Wallet Operations</h1>
        <div>
          <label style={{ marginRight: 8, fontWeight: 'bold' }}>User ID:</label>
          <select value={userId} onChange={e => setUserId(e.target.value)} style={{ padding: '6px 12px' }}>
            <option value="1">User 1</option>
            <option value="2">User 2</option>
          </select>
        </div>
      </header>

      <section style={{ background: '#f4f4f5', padding: '16px 20px', borderRadius: 8, marginBottom: 20 }}>
        <h3>Current Balance</h3>
        <p style={{ fontSize: '24px', fontWeight: 'bold', margin: '4px 0 0 0' }}>${balance}</p>
      </section>

      <p>Transaction history for active tenant session</p>
      {error && <p role="alert" style={{ color: 'red' }}>{error}</p>}

      <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse', marginTop: 10 }}>
        <thead>
          <tr style={{ borderBottom: '2px solid #ddd' }}>
            <th style={{ padding: 8 }}>Reference</th>
            <th style={{ padding: 8 }}>Type</th>
            <th style={{ padding: 8 }}>Amount</th>
            <th style={{ padding: 8 }}>Status</th>
          </tr>
        </thead>
        <tbody>
          {items.map(t => (
            <tr key={t.id} onClick={() => setSelected(t)} style={{ cursor: 'pointer', borderBottom: '1px solid #eee' }}>
              <td style={{ padding: 8 }}>{t.reference}</td>
              <td style={{ padding: 8 }}>{t.kind}</td>
              <td style={{ padding: 8 }}>${t.amount}</td>
              <td style={{ padding: 8 }}>{t.status}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {selected && (
        <section style={{ marginTop: 20, padding: 16, border: '1px solid #ccc', borderRadius: 8, background: '#fafafa' }}>
          <h2>Transaction #{selected.id}</h2>
          <p><strong>Status:</strong> {selected.status}</p>
          <p><strong>Reference:</strong> {selected.reference}</p>
          <p><strong>Failure Reason:</strong> {selected.failure_reason || '—'}</p>
          <button onClick={() => setSelected(null)} style={{ marginTop: 10, padding: '6px 12px' }}>Close</button>
        </section>
      )}
    </main>
  );
}

createRoot(document.getElementById('root')!).render(<React.StrictMode><App /></React.StrictMode>);