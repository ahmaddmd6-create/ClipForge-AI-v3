import { FileText } from 'lucide-react';

export default function TermsAndConditions() {
  return (
    <div className="container" style={{ maxWidth: '820px' }}>
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
          <FileText size={26} />
          <h1>Terms & Conditions</h1>
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Effective date: October 12, 2026</p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', fontSize: '0.925rem', lineHeight: 1.6 }}>
        <section className="card">
          <h2>1. Content Rights and Authorization</h2>
          <p style={{ marginTop: '0.5rem' }}>
            By using ClipForge AI, you agree that you are solely responsible for verifying that you hold the legal right, ownership, or authorized license to process any video submitted via URL or local file upload.
          </p>
          <p style={{ marginTop: '0.5rem' }}>
            ClipForge AI is designed for lawful content creation, podcast editing, educational commentary, and authorized media repurposing. You must not use this tool to bypass DRM, circumvent copyright protections, or process content in violation of third-party platform terms of service.
          </p>
        </section>

        <section className="card">
          <h2>2. Technical Limitations & Disclaimers</h2>
          <p style={{ marginTop: '0.5rem' }}>
            ClipForge AI performs speech transcription and video rendering locally using CPU resources. Processing speed depends on your host computer's hardware. The software is provided "as is", without warranty of any kind, express or implied.
          </p>
        </section>

        <section className="card">
          <h2>3. Prohibited Uses</h2>
          <p style={{ marginTop: '0.5rem' }}>
            You agree not to use ClipForge AI to process defamatory, unlawful, sexually explicit, or infringing content. You agree not to distribute modified media without adhering to applicable intellectual property laws.
          </p>
        </section>

        <section className="card">
          <h2>4. Governing Law</h2>
          <p style={{ marginTop: '0.5rem' }}>
            These terms are governed by applicable Indian laws and the jurisdiction of courts in India.
          </p>
        </section>
      </div>
    </div>
  );
}
