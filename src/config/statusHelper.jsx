import React from 'react';

export function getStatusInfo(status) {
  const raw = (status || 'مفتوح').toString().trim();
  const lower = raw.toLowerCase();

  // 1. English Status (e.g. Freelancer.com)
  if (lower === 'open' || lower === 'active') {
    return {
      key: 'open',
      label: 'Open',
      fullLabel: 'Open for Bidding'
    };
  }
  if (lower === 'in progress' || lower === 'pending' || lower === 'in_progress' || lower === 'custom') {
    return {
      key: 'in-progress',
      label: 'In Progress',
      fullLabel: 'In Progress'
    };
  }
  if (lower === 'completed' || lower === 'closed' || lower === 'complete' || lower === 'frozen') {
    return {
      key: 'completed',
      label: 'Completed',
      fullLabel: 'Completed'
    };
  }

  // 2. Arabic Status (Khamsat, Mostaql, Nafezly)
  if (raw.includes('تنفيذ') || raw.includes('تقدم') || raw.includes('جاري')) {
    return {
      key: 'in-progress',
      label: 'تحت التنفيذ',
      fullLabel: 'تحت التنفيذ (In Progress)'
    };
  }
  if (raw.includes('مكتمل') || raw.includes('مغلق') || raw.includes('منتهي') || raw.includes('ملغي')) {
    return {
      key: 'completed',
      label: 'مكتمل',
      fullLabel: 'مكتمل / مغلق'
    };
  }
  return {
    key: 'open',
    label: 'مفتوح',
    fullLabel: 'مفتوح لتلقي العروض'
  };
}

export function StatusPill({ status }) {
  const info = getStatusInfo(status);
  return (
    <span className={`clean-status-pill ${info.key}`} title={`حالة المشروع: ${info.label}`}>
      <span className="status-live-dot" />
      {info.label}
    </span>
  );
}

export function StatusDetailTag({ status }) {
  const info = getStatusInfo(status);
  return (
    <span className={`detail-status-tag ${info.key}`} title={`حالة المشروع: ${info.fullLabel}`}>
      <span className="status-live-dot" />
      {info.fullLabel}
    </span>
  );
}
