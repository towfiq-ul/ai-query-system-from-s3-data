import React, {useState} from "react";

/** @param {{ source: {s3_key: string, file_type: string, chunk_index: number, score: number, excerpt: string} }} */
export function SourceCard({source}) {
    const [expanded, setExpanded] = useState(false);
    const filename = source.s3_key.split("/").pop();
    const scorePercent = Math.round(source.score * 100);

    return (
        <div style={styles.card}>
            <div style={styles.header} onClick={() => setExpanded((v) => !v)}>
                <div style={styles.meta}>
                    <span style={styles.badge}>{source.file_type.toUpperCase()}</span>
                    <span style={styles.filename} title={source.s3_key}>{filename}</span>
                    <span style={styles.chunk}>chunk #{source.chunk_index}</span>
                </div>
                <div style={styles.right}>
                    <span style={styles.score}>{scorePercent}% match</span>
                    <span style={styles.toggle}>{expanded ? "▲" : "▼"}</span>
                </div>
            </div>
            {expanded && <p style={styles.excerpt}>{source.excerpt}</p>}
        </div>
    );
}

const styles = {
    card: {background: "#1e2130", borderRadius: 8, marginTop: 6, overflow: "hidden", fontSize: 13},
    header: {
        display: "flex", justifyContent: "space-between", alignItems: "center",
        padding: "8px 12px", cursor: "pointer", userSelect: "none"
    },
    meta: {display: "flex", alignItems: "center", gap: 8, overflow: "hidden"},
    badge: {
        background: "#2d6cdf", color: "#fff", borderRadius: 4, padding: "2px 6px",
        fontSize: 11, fontWeight: 700, flexShrink: 0
    },
    filename: {color: "#a0aec0", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis"},
    chunk: {color: "#4a5568", flexShrink: 0},
    right: {display: "flex", alignItems: "center", gap: 10, flexShrink: 0},
    score: {color: "#68d391", fontWeight: 600},
    toggle: {color: "#718096", fontSize: 10},
    excerpt: {
        margin: 0, padding: "8px 12px 12px", color: "#cbd5e0",
        borderTop: "1px solid #2d3748", lineHeight: 1.6
    },
};
