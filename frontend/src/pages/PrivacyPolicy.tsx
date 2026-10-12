import { Shield } from 'lucide-react';

const BUSINESS = {
  name: 'ClipForge AI Open Source Project',
  registeredAddress: 'Local Deployment / On-Premise',
  contactEmail: 'support@clipforge.local',
  grievanceEmail: 'privacy@clipforge.local',
  grievanceName: 'Data Protection Officer',
  website: 'http://localhost:8080',
  effectiveDate: '2026-10-12',
  lastUpdated: '2026-10-12',
};

export default function PrivacyPolicy() {
  return (
    <div className="container" style={{ maxWidth: '820px' }}>
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
          <Shield size={26} />
          <h1>Privacy Policy</h1>
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          Effective date: {BUSINESS.effectiveDate} • Last updated: {BUSINESS.lastUpdated}
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', fontSize: '0.925rem', lineHeight: 1.6 }}>
        <section className="card">
          <h2>1. Overview & Data Minimization</h2>
          <p style={{ marginTop: '0.5rem' }}>
            ClipForge AI is an autonomous, local-first video-processing engine. The application operates directly on your local machine and containerized environment. We adhere strictly to data minimization: we do not collect or transmit your video files, transcripts, or personal data to remote advertising networks or unauthorized third parties.
          </p>
        </section>

        <section className="card">
          <h2>2. India DPDP Act, 2023 Compliance</h2>
          <p style={{ marginTop: '0.5rem' }}>
            Under the Digital Personal Data Protection Act, 2023 (India) ("DPDP Act"), processing of personal data is governed by principles of lawful purpose, notice, and user consent:
          </p>
          <ul style={{ paddingLeft: '1.25rem', marginTop: '0.5rem', display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
            <li><strong>Local Processing:</strong> Speech recognition (faster-whisper) and video rendering (FFmpeg) occur locally on your machine.</li>
            <li><strong>Purpose Limitation:</strong> Source media and transcripts are processed exclusively for the purpose of identifying clips and rendering vertical video output requested by you.</li>
            <li><strong>Right to Erasure:</strong> You retain complete control over your data. Deleting a job or clip immediately removes all corresponding files from disk storage.</li>
          </ul>
        </section>

        <section className="card">
          <h2>3. Media Source & Third-Party Integrations</h2>
          <p style={{ marginTop: '0.5rem' }}>
            When providing a YouTube URL, metadata is inspected via standard YouTube interfaces. No login credentials or DRM-protected streams are bypassed. Users must confirm source rights prior to processing.
          </p>
        </section>

        <section className="card">
          <h2>4. Retention Policy</h2>
          <p style={{ marginTop: '0.5rem' }}>
            All inputs, generated clips, transcripts, and manifests are saved strictly in your local <code>storage/outputs</code> and <code>storage/inputs</code> directories on your host computer. Output retention defaults to 30 days and can be customized in the Storage & Settings page.
          </p>
        </section>

        <section className="card">
          <h2>5. Contact & Inquiries</h2>
          <p style={{ marginTop: '0.5rem' }}>
            For privacy inquiries or data governance requests regarding ClipForge AI, contact: <strong>{BUSINESS.contactEmail}</strong>.
          </p>
        </section>
      </div>
    </div>
  );
}
