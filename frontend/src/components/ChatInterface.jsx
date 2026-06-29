import React, {useState, useRef, useEffect} from "react";
import {useChat} from "../hooks/useChat";
import {MessageBubble} from "./MessageBubble";
import {triggerIndex} from "../utils/api";

export function ChatInterface() {
    const {messages, loading, ask, clear} = useChat();
    const [input, setInput] = useState("");
    const [topK, setTopK] = useState(5);
    const [showIndex, setShowIndex] = useState(false);
    const [indexForm, setIndexForm] = useState({bucket: "", prefix: "", force: false});
    const [indexMsg, setIndexMsg] = useState(null);
    const bottomRef = useRef(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({behavior: "smooth"});
    }, [messages, loading]);

    const handleSend = () => {
        if (!input.trim() || loading) return;
        ask(input.trim(), {topK});
        setInput("");
    };

    const handleKeyDown = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleIndex = async () => {
        setIndexMsg("Indexing…");
        try {
            const result = await triggerIndex(indexForm.bucket, indexForm.prefix, indexForm.force);
            setIndexMsg(result.message);
        } catch {
            setIndexMsg("Indexing failed. Check API logs.");
        }
    };

    return (
        <div style={styles.root}>
            {/* Header */}
            <header style={styles.header}>
                <div style={styles.logo}>
                    <span style={styles.logoIcon}>⬡</span>
                    <span style={styles.logoText}>S3 Search</span>
                </div>
                <div style={styles.controls}>
                    <label style={styles.label}>Top K</label>
                    <select style={styles.select} value={topK} onChange={(e) => setTopK(+e.target.value)}>
                        {[3, 5, 10, 15].map((n) => <option key={n}>{n}</option>)}
                    </select>
                    <button style={styles.ghostBtn} onClick={() => setShowIndex((v) => !v)}>
                        Index Docs
                    </button>
                    <button style={styles.ghostBtn} onClick={clear}>Clear</button>
                </div>
            </header>

            {/* Index panel */}
            {showIndex && (
                <div style={styles.indexPanel}>
                    <h3 style={styles.indexTitle}>Index S3 Bucket</h3>
                    <div style={styles.indexRow}>
                        <input style={styles.input} placeholder="Bucket name"
                               value={indexForm.bucket}
                               onChange={(e) => setIndexForm((f) => ({...f, bucket: e.target.value}))}/>
                        <input style={styles.input} placeholder="Prefix (optional)"
                               value={indexForm.prefix}
                               onChange={(e) => setIndexForm((f) => ({...f, prefix: e.target.value}))}/>
                        <label style={styles.checkLabel}>
                            <input type="checkbox" checked={indexForm.force}
                                   onChange={(e) => setIndexForm((f) => ({...f, force: e.target.checked}))}/>
                            Force re-index
                        </label>
                        <button style={styles.primaryBtn} onClick={handleIndex}>Run</button>
                    </div>
                    {indexMsg && <p style={styles.indexMsg}>{indexMsg}</p>}
                </div>
            )}

            {/* Messages */}
            <div style={styles.messages}>
                {messages.length === 0 && (
                    <div style={styles.empty}>
                        <p style={styles.emptyTitle}>Ask anything about your S3 documents</p>
                        <p style={styles.emptyHint}>Supports PDF, TXT, CSV, JSON, and MD files</p>
                    </div>
                )}
                {messages.map((msg, i) => <MessageBubble key={i} message={msg}/>)}
                {loading && (
                    <div style={styles.typingWrap}>
                        <div style={styles.typing}>
                            <span/><span/><span/>
                        </div>
                    </div>
                )}
                <div ref={bottomRef}/>
            </div>

            {/* Input */}
            <div style={styles.inputRow}>
        <textarea
            style={styles.textarea}
            rows={1}
            placeholder="Ask a question about your documents…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
        />
                <button style={{...styles.sendBtn, opacity: loading || !input.trim() ? 0.4 : 1}}
                        onClick={handleSend} disabled={loading || !input.trim()}>
                    ↑
                </button>
            </div>
        </div>
    );
}

const styles = {
    root: {
        display: "flex", flexDirection: "column", height: "100vh",
        background: "#0f1117", color: "#e2e8f0", fontFamily: "'Inter', sans-serif"
    },
    header: {
        display: "flex", justifyContent: "space-between", alignItems: "center",
        padding: "14px 24px", borderBottom: "1px solid #1e2130", flexShrink: 0
    },
    body: {
        scrollbars: "none"
    },
    logo: {display: "flex", alignItems: "center", gap: 10},
    logoIcon: {fontSize: 22, color: "#2d6cdf"},
    logoText: {fontWeight: 700, fontSize: 18, letterSpacing: "-0.3px"},
    controls: {display: "flex", alignItems: "center", gap: 12},
    label: {fontSize: 13, color: "#718096"},
    select: {
        background: "#1a1f2e", color: "#e2e8f0", border: "1px solid #2d3748",
        borderRadius: 6, padding: "4px 8px", fontSize: 13
    },
    ghostBtn: {
        background: "transparent", color: "#a0aec0", border: "1px solid #2d3748",
        borderRadius: 6, padding: "5px 12px", fontSize: 13, cursor: "pointer"
    },
    indexPanel: {
        background: "#1a1f2e", borderBottom: "1px solid #2d3748",
        padding: "16px 24px", flexShrink: 0
    },
    indexTitle: {margin: "0 0 12px", fontSize: 15, fontWeight: 600},
    indexRow: {display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap"},
    input: {
        background: "#0f1117", border: "1px solid #2d3748", color: "#e2e8f0",
        borderRadius: 6, padding: "6px 10px", fontSize: 13, minWidth: 180
    },
    checkLabel: {fontSize: 13, color: "#a0aec0", display: "flex", gap: 6, alignItems: "center"},
    primaryBtn: {
        background: "#2d6cdf", color: "#fff", border: "none", borderRadius: 6,
        padding: "6px 16px", fontSize: 13, cursor: "pointer", fontWeight: 600
    },
    indexMsg: {marginTop: 8, fontSize: 13, color: "#68d391"},
    messages: {flex: 1, overflowY: "auto", padding: "24px 24px 0"},
    empty: {
        display: "flex", flexDirection: "column", alignItems: "center",
        justifyContent: "center", height: "60%", gap: 8
    },
    emptyTitle: {fontSize: 18, fontWeight: 600, color: "#a0aec0", margin: 0},
    emptyHint: {fontSize: 14, color: "#4a5568", margin: 0},
    typingWrap: {display: "flex", marginBottom: 16},
    typing: {
        background: "#1a1f2e", borderRadius: 12, padding: "14px 18px",
        display: "flex", gap: 5, alignItems: "center"
    },
    inputRow: {
        display: "flex", gap: 10, padding: "16px 24px", borderTop: "1px solid #1e2130",
        flexShrink: 0
    },
    textarea: {
        flex: 1, background: "#1a1f2e", border: "1px solid #2d3748", color: "#e2e8f0",
        borderRadius: 10, padding: "10px 14px", fontSize: 15, resize: "none",
        lineHeight: 1.5, outline: "none"
    },
    sendBtn: {
        width: 42, height: 42, background: "#2d6cdf", color: "#fff", border: "none",
        borderRadius: 10, fontSize: 20, cursor: "pointer", alignSelf: "flex-end",
        display: "flex", alignItems: "center", justifyContent: "center"
    },
};
