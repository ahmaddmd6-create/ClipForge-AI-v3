import { HelpCircle } from 'lucide-react';

export default function RefundPolicy() {
  return (
    <div className="container" style={{ maxWidth: '820px' }}>
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
          <HelpCircle size={26} />
          <h1>Refund Information</h1>
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Effective date: October 12, 2026</p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', fontSize: '0.925rem', lineHeight: 1.6 }}>
        <section className="card">
          <h2>Free Local Application (Not Applicable)</h2>
          <p style={{ marginTop: '0.5rem' }}>
            ClipForge AI is an open-source, local-first application designed for on-premise execution on your own computer or Docker infrastructure.
          </p>
          <p style={{ marginTop: '0.5rem' }}>
            We do not sell subscriptions, user credits, or paid services through this software, nor do we process monetary transactions. Therefore, refunds are not applicable.
          </p>
        </section>

        <section className="card">
          <h2>Future Paid Services</h2>
          <p style={{ marginTop: '0.5rem' }}>
            If commercial hosted cloud rendering or paid transcription credits are introduced in the future, a comprehensive refund policy adhering to consumer protection laws will be published prior to accepting any payments.
          </p>
        </section>
      </div>
    </div>
  );
}
