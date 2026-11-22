import React from 'react';
import { BookOpen, HelpCircle } from 'lucide-react';

function cleanText(str) {
  if (str === null || str === undefined) return '';
  const val = typeof str !== 'string' ? String(str) : str;
  return val
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/^#+\s*/gm, '')
    .replace(/[\u2013\u2014]/g, ' - ')
    .replace(/`/g, '')
    .trim();
}

export default function HumanReadableLegalCard({
  title,
  tag,
  tagType = 'gold', // 'gold', 'navy', 'pass', 'warn', 'alert'
  whatItMeans,
  citation,
  additionalNotes
}) {
  return (
    <div className="legal-item-box">
      {/* Box Header */}
      <div className="legal-item-box-header">
        <h4 style={{
          fontSize: '1.05rem',
          fontWeight: 700,
          color: 'var(--court-navy)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          {cleanText(title)}
        </h4>
        {tag && (
          <span className={`badge-pill badge-${tagType}`}>
            {cleanText(tag)}
          </span>
        )}
      </div>

      {/* Box Content: What it means & Legal Source / Citation */}
      <div className="legal-item-box-body">
        {/* What it means */}
        <div className="what-it-means-block">
          <div className="what-it-means-label">
            <HelpCircle size={14} />
            WHAT IT MEANS (PLAIN LANGUAGE)
          </div>
          <div className="what-it-means-text">
            {cleanText(whatItMeans)}
          </div>
        </div>

        {/* Legal Source / Citation */}
        <div className="legal-source-block">
          <div className="legal-source-label">
            <BookOpen size={14} />
            LEGAL SOURCE / CITATION
          </div>
          <div className="legal-source-content">
            {cleanText(citation)}
          </div>
        </div>

        {additionalNotes && (
          <div style={{
            fontSize: '12.5px',
            color: 'var(--ink-secondary)',
            fontStyle: 'italic',
            paddingLeft: '0.5rem',
            borderLeft: '2px solid var(--court-parchment-border)'
          }}>
            {cleanText(additionalNotes)}
          </div>
        )}
      </div>
    </div>
  );
}
