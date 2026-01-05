import React, { useState } from "react";

function highlightPharse(text, query) {
    if (!query || !text) return text;

    const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const regex = new RegExp(`(${escaped})`, "gi");

    return text.replace(regex, "<mark>$1</mark>");
}


function Search() {
    const [query, setQuery] = useState("");
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [k, setK] = useState(5);

    const handleSearch = async () => {
        if (!query.trim()) return;

        setLoading(true);

        try {
            const response = await fetch("http://localhost:8000/full_search", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    query: query,
                    k: k
                })
            });

            const data = await response.json();
            setResults(data.results || []);
        } catch (error) {
            console.error("Error al buscar:", error);
        }

        setLoading(false);
    };

    return (
        <div style = {styles.container}>
            <h1 style = {styles.title}>Buscador RI</h1>

            <div style = {styles.searchBox}>
                <input
                    type = "text"
                    placeholder = "Escribe tu consulta..."
                    value = {query}
                    onChange = {(e) => setQuery(e.target.value)}
                    style = {styles.input}
                    onKeyDown = {(e) => e.key === "Enter" && handleSearch()}
                />
                <button onClick = {handleSearch} style = {styles.button}>
                    Buscar
                </button>
            </div>

            <div style={{ marginBottom: "30px", textAlign: "center" }}>
                <label style={{ fontSize: "14px", color: "#444" }}>
                    Número de resultados :&nbsp;
                    <input
                        type="number"
                        min="1"
                        max="50"
                        value={k}
                        onChange={(e) => setK(Number(e.target.value))}
                        style={{
                            width: "70px",
                            padding: "6px",
                            marginLeft: "8px",
                            borderRadius: "6px",
                            border: "1px solid #ccc",
                            textAlign: "center"
                        }}
                    />
                </label>
            </div>


            {loading && <p style={{ textAlign: "center" }}>Buscando documentos...</p>}

            <div style = {styles.results}>
                {results.length === 0 && !loading && (
                    <p style={{ textAlign: "center", color: "#666" }}>
                        No se han encontrado resultados
                    </p>
                )}
                
                {results.map((item, index) => (
                    <div key={index} style={styles.card}>
                        <h3 style={{ marginBottom: "8px" }}>
                            #{index + 1} — {item.doc_name}
                        </h3>
                        <p style={{ margin: 0, color: "#555" }}>
                            <strong>Similitud:</strong> {item.score.toFixed(4)}
                        </p>
                        
                        {item.snippet && (
                            <p
                                style={{
                                    marginTop: "12px",
                                    color: "#444",
                                    fontSize: "14px",
                                    lineHeight: "1.6"
                                }}
                                dangerouslySetInnerHTML={{
                                    __html: `<strong>Fragmento relevante:</strong><br/>${highlightPharse(
                                        item.snippet,
                                        query
                                    )}`
                                }}
                            />
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}

export default Search;

const styles = {
    container: {
        maxWidth: "900px",
        margin: "40px auto",
        padding: "40px",
        fontFamily: "'Segoe UI', Roboto, sans-serif",
        backgroundColor: "#ffffff",
        borderRadius: "12px",
        boxShadow: "0 10px 30px rgba(0,0,0,0.08)"
    },
    title: {
        textAlign: "center",
        marginBottom: "40px",
        fontSize: "32px",
        fontWeight: "600",
        color: "#222"
    },
    searchBox: {
        display: "flex",
        gap: "10px",
        marginBottom: "40px"
    },
    input: {
        flex: 1,
        padding: "14px",
        fontSize: "16px",
        borderRadius: "8px",
        border: "1px solid #ccc",
        outline: "none"
    },
    button: {
        padding: "14px 24px",
        fontSize: "16px",
        fontWeight: "600",
        borderRadius: "8px",
        border: "none",
        cursor: "pointer",
        backgroundColor: "#2563eb",
        color: "#ffffff",
        transition: "background-color 0.2s ease"
    },
    results: {
        marginTop: "20px"
    },
    card: {
        border: "1px solid #e5e7eb",
        borderRadius: "10px",
        padding: "20px",
        marginBottom: "15px",
        backgroundColor: "#f9fafb"
    }
};