import React from "react";
import { SourceCard } from "./SourceCard";

/** @param {{ message: import("../hooks/useChat").Message }} */
export function MessageBubble({ message }) {
  const isUser = message.role === "user";
  return (
    <div style={{ ...styles.wrapper, justifyContent: isUser ? "flex-end" : "flex-start" }}>
      <div style={{ ...styles.bubble, ...(isUser ? styles.user : styles.assistant) }}>
        <p style={styles.text}>{message.content}</p>

        {!isUser && message.sources?.length > 0 && (
          <div style={styles.sources}>
            <p style={styles.sourcesLabel}>
              {message.sources.length} source{message.sources.length > 1 ? "s" : ""}
              {message.cached && <span style={styles.cachedBadge}>cached</span>}
              {message.latency_ms && (
                <span style={styles.latency}>{message.latency_ms}ms</span>
              )}
            </p>
            {message.sources.map((s, i) => (
              <SourceCard key={`${s.s3_key}-${s.chunk_index}-${i}`} source={s} />
            ))}
          </div>
        )}

        {!isUser && !message.sources?.length && message.latency_ms && (
          <p style={styles.latency}>{message.latency_ms}ms</p>
        )}
      </div>
    </div>
  );
}

const styles = {
  wrapper:      { display: "flex", marginBottom: 16 },
  bubble:       { maxWidth: "78%", borderRadius: 12, padding: "12px 16px" },
  user:         { background: "#2d6cdf", color: "#fff", borderBottomRightRadius: 2 },
  assistant:    { background: "#1a1f2e", color: "#e2e8f0", borderBottomLeftRadius: 2 },
  text:         { margin: 0, lineHeight: 1.65, whiteSpace: "pre-wrap" },
  sources:      { marginTop: 10 },
  sourcesLabel: { margin: "0 0 4px", fontSize: 12, color: "#718096", display: "flex",
                   alignItems: "center", gap: 8 },
  cachedBadge:  { background: "#2d3748", color: "#68d391", borderRadius: 4,
                   padding: "1px 6px", fontSize: 11, fontWeight: 600 },
  latency:      { color: "#4a5568", fontSize: 11 },
};
