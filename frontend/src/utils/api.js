import axios from "axios";

function getTimeout() {
    const rawTimeout = import.meta.env.VITE_API_TIMEOUT;
    const timeoutSeconds = rawTimeout !== undefined ? parseInt(rawTimeout) : null;
    return timeoutSeconds !== null ? timeoutSeconds * 1_000 : false
}

const client = axios.create({
    baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
    headers: {"Content-Type": "application/json"},
    timeout: getTimeout() || 150_000
});

/**
 * @param {string} question
 * @param {number} topK
 * @param {boolean} includeSources
 * @returns {Promise<{answer: string, sources: Array, cached: boolean, latency_ms: number}>}
 */
export async function sendQuery(question, topK = 5, includeSources = true) {
    const {data} = await client.post("/api/query", {
        question,
        top_k: topK,
        include_sources: includeSources,
    });
    return data;
}

/**
 * @param {string} bucket
 * @param {string} prefix
 * @param {boolean} forceReindex
 */
export async function triggerIndex(bucket, prefix = "", forceReindex = false) {
    const {data} = await client.post("/api/index", {
        bucket,
        prefix,
        force_reindex: forceReindex,
    });
    return data;
}

export async function fetchHealth() {
    const {data} = await client.get("/api/health");
    return data;
}
