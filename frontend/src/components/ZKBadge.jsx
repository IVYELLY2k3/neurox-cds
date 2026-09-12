import React from 'react';
import { ShieldCheck } from 'lucide-react';

export default function ZKBadge({ proofId, statement, compact = false }) {
  if (compact) {
    return (
      <span className="zk-badge" title={statement || 'Verified via Zero-Knowledge Proof'}>
        <ShieldCheck size={12} className="zk-badge-icon" />
        ZK
      </span>
    );
  }

  return (
    <span
      className="zk-badge"
      title={proofId ? `Proof ID: ${proofId}` : 'Zero-Knowledge Verified'}
    >
      <ShieldCheck size={12} className="zk-badge-icon" />
      ZK Verified
    </span>
  );
}
