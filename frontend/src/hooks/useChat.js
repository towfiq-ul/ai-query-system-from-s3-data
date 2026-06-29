import {useState, useCallback} from "react";
import {sendQuery} from "../utils/api";

/**
 * @typedef {{ role: "user"|"assistant", content: string, sources?: Array, latency_ms?: number, cached?: boolean }} Message
 */

export function useChat() {
    const [messages, setMessages] = useState(/** @type {Message[]} */ ([]));
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const append = useCallback((msg) => setMessages((prev) => [...prev, msg]), []);

    const ask = useCallback(
        async (question, {topK = 5, includeSources = true} = {}) => {
            if (!question.trim()) return;
            setError(null);
            append({role: "user", content: question});
            setLoading(true);

            try {
                const result = await sendQuery(question, topK, includeSources);
                append({
                    role: "assistant",
                    content: result.answer,
                    sources: result.sources,
                    latency_ms: result.latency_ms,
                    cached: result.cached,
                });
            } catch (err) {
                const errMsg = err?.response?.data?.detail[0]?.msg;
                const message = errMsg || "Request failed. Is the API running?";
                setError(message);
                append({role: "assistant", content: `⚠️ ${message}`});
            } finally {
                setLoading(false);
            }
        },
        [append]
    );

    const clear = useCallback(() => {
        setMessages([]);
        setError(null);
    }, []);

    return {messages, loading, error, ask, clear};
}
