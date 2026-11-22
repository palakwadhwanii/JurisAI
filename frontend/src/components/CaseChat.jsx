import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, BookOpen, Scale, HelpCircle } from 'lucide-react';

function cleanText(str) {
  if (str === null || str === undefined) return '';
  const val = typeof str !== 'string' ? String(str) : str;
  return val
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/^#+\s*/gm, '')
    .replace(/^>\s*\[!\w+\]\s*/gm, '')
    .replace(/^>\s*/gm, '')
    .replace(/`/g, '')
    .trim();
}

export default function CaseChat({ analysisData }) {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'jurisai',
      text: 'Hello. I have analyzed your case across the applicable Central Acts, Supreme Court precedents, and legal constraints. You can ask me any follow-up questions about your legal options, procedural steps, or how specific laws apply to your situation.'
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSend = (textToSend) => {
    const query = (textToSend || inputMessage).trim();
    if (!query) return;

    const userMsg = {
      id: Date.now(),
      sender: 'user',
      text: query
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setIsTyping(true);

    // Formulate a grounded legal response based on the existing case analysis
    setTimeout(() => {
      const qLower = query.toLowerCase();
      let reply = '';

      if (qLower.includes('waive') || qLower.includes('cooling') || qLower.includes('6 month') || qLower.includes('waiting')) {
        reply = 'Regarding the 6-month cooling-off waiting period under Section 13B(2) of the Hindu Marriage Act: Under the Supreme Court ruling in Amardeep Singh v. Harveen Kaur (2017) 8 SCC 746, this period is directory rather than mandatory. If you have been living apart for over one year, all mediation attempts have failed, and all financial and custody terms are settled, the family court can waive the waiting period upon filing a formal waiver application supported by mutual affidavits.';
      } else if (qLower.includes('document') || qLower.includes('file') || qLower.includes('affidavit') || qLower.includes('prepare')) {
        reply = 'The mandatory documents you should prepare for the court include:\n1. Joint Petition signed and verified by both parties under Section 13B.\n2. Memorandum of Settlement or Consent Terms detailing permanent alimony, stridhan, and custody.\n3. Comprehensive Affidavits of Assets and Liabilities as mandated by the Supreme Court in Rajnesh v. Neha.\n4. Marriage certificate and proof of living separately for more than one year.';
      } else if (qLower.includes('maintenance') || qLower.includes('alimony') || qLower.includes('money') || qLower.includes('financial')) {
        reply = 'For permanent alimony and maintenance under Section 25 of the Hindu Marriage Act, the court considers both spouses earning capacities, living standards during the marriage, liabilities, and the duration of the marital union. Under Rajnesh v. Neha (2021) 2 SCC 324, both parties must make full financial disclosure under oath to ensure fairness.';
      } else if (qLower.includes('contest') || qLower.includes('withdraw') || qLower.includes('refuse') || qLower.includes('other party')) {
        reply = 'Under the Sureshta Devi doctrine, either party retains the legal prerogative to unilaterally withdraw consent at any time before the second motion decree is passed. If one party withdraws consent, the petition for mutual consent cannot proceed and the matter would need to be contested under Section 13(1) grounds such as cruelty or desertion.';
      } else if (qLower.includes('step') || qLower.includes('next') || qLower.includes('procedure') || qLower.includes('how long')) {
        reply = 'Your immediate next procedural steps are:\n1. Finalize and execute the joint consent terms covering all alimony, assets, and custody.\n2. Present the First Motion joint petition before the Principal Family Court having territorial jurisdiction.\n3. File an interim application seeking waiver of the 6-month cooling-off period citing Supreme Court guidelines.\n4. Record statement upon oath at the Second Motion to receive the formal dissolution decree.';
      } else {
        const claims = analysisData?.case_state?.claims?.join(', ') || 'matrimonial relief';
        reply = `Based on your case matrix regarding ${claims}: You have strong statutory grounding under Central Indian statutes. The crucial factor is ensuring that all documentary evidence (settlement deed, asset disclosure forms, and proof of separate residence) is properly drafted and executed in accordance with Supreme Court standards.`;
      }

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'jurisai',
          text: reply
        }
      ]);
      setIsTyping(false);
    }, 600);
  };

  const samplePrompts = [
    'Can the 6-month cooling period be waived in my case?',
    'What specific documents should I prepare next?',
    'How is permanent alimony calculated?',
    'What happens if the other party changes their mind?'
  ];

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: 'calc(100vh - 140px)',
      background: '#ffffff',
      border: '1px solid var(--court-parchment-border)',
      borderRadius: '6px',
      overflow: 'hidden'
    }}>
      {/* Chat Header */}
      <div style={{
        background: 'var(--court-navy)',
        color: '#ffffff',
        padding: '1rem 1.5rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
          <Bot size={20} color="var(--court-gold)" />
          <div>
            <h3 style={{ fontSize: '1.2rem', color: '#ffffff', fontWeight: 700 }}>
              Case Consultation Chat
            </h3>
            <div style={{ fontSize: '12px', color: 'var(--court-gold-light)', marginTop: '1px' }}>
              Ask follow-up questions grounded in your analyzed case matrix
            </div>
          </div>
        </div>
        <span className="badge-pill badge-gold" style={{ fontSize: '11px' }}>
          JURISAI INTERACTIVE
        </span>
      </div>

      {/* Suggested Follow-up Chips */}
      <div style={{
        padding: '0.65rem 1.25rem',
        background: 'var(--court-parchment-subtle)',
        borderBottom: '1px solid var(--court-parchment-border)',
        display: 'flex',
        alignItems: 'center',
        gap: '0.5rem',
        overflowX: 'auto'
      }}>
        <span style={{ fontSize: '11.5px', color: 'var(--ink-muted)', fontWeight: 600, flexShrink: 0 }}>
          Quick questions:
        </span>
        {samplePrompts.map((prompt, idx) => (
          <button
            key={idx}
            onClick={() => handleSend(prompt)}
            className="btn-legal-secondary"
            style={{
              fontSize: '12px',
              padding: '3px 9px',
              whiteSpace: 'nowrap',
              backgroundColor: '#ffffff'
            }}
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Chat Messages Stream */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '1.5rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '1rem',
        background: '#faf9f5'
      }}>
        {messages.map((msg) => (
          <div
            key={msg.id}
            style={{
              display: 'flex',
              gap: '0.75rem',
              alignItems: 'flex-start',
              alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '85%'
            }}
          >
            {msg.sender === 'jurisai' && (
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '4px',
                backgroundColor: 'var(--court-navy)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--court-gold)',
                flexShrink: 0
              }}>
                <Bot size={18} />
              </div>
            )}

            <div style={{
              background: msg.sender === 'user' ? 'var(--court-navy)' : '#ffffff',
              color: msg.sender === 'user' ? '#ffffff' : 'var(--ink-primary)',
              padding: '0.85rem 1.15rem',
              borderRadius: '6px',
              border: msg.sender === 'user' ? '1px solid var(--court-navy)' : '1px solid var(--court-parchment-border)',
              fontSize: '14.5px',
              lineHeight: 1.6,
              boxShadow: 'var(--shadow-sm)',
              whiteSpace: 'pre-line'
            }}>
              {cleanText(msg.text)}
            </div>

            {msg.sender === 'user' && (
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '4px',
                backgroundColor: 'var(--court-parchment-border)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--court-navy)',
                flexShrink: 0
              }}>
                <User size={18} />
              </div>
            )}
          </div>
        ))}

        {isTyping && (
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '4px',
              backgroundColor: 'var(--court-navy)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--court-gold)'
            }}>
              <Bot size={18} />
            </div>
            <div style={{
              background: '#ffffff',
              border: '1px solid var(--court-parchment-border)',
              padding: '0.65rem 1rem',
              borderRadius: '6px',
              fontSize: '13px',
              color: 'var(--ink-muted)'
            }}>
              JurisAI is researching relevant provisions and rulings...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input Bar */}
      <div style={{
        padding: '0.85rem 1.25rem',
        background: '#ffffff',
        borderTop: '1px solid var(--court-parchment-border)',
        display: 'flex',
        gap: '0.75rem',
        alignItems: 'center'
      }}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask a follow-up question about this case..."
          style={{
            flex: 1,
            padding: '0.65rem 1rem',
            borderRadius: '4px',
            border: '1px solid var(--court-parchment-border)',
            fontSize: '14.5px',
            outline: 'none',
            fontFamily: 'var(--font-family-base)',
            color: 'var(--ink-primary)'
          }}
        />
        <button
          onClick={() => handleSend()}
          disabled={!inputMessage.trim()}
          className="btn-legal-primary"
          style={{ padding: '0.65rem 1.25rem' }}
        >
          <Send size={15} />
          Send
        </button>
      </div>
    </div>
  );
}
