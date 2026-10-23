
"use client";

import { FormEvent, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Send, Bot, User, LoaderCircle } from "lucide-react";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const message = input.trim();
    if (!message || loading) return;

    setInput("");
    setError("");
    setLoading(true);

    setMessages((previous) => [
      ...previous,
      { role: "user", content: message },
    ]);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/chat`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message }),
        },
      );

      if (!response.ok) {
        throw new Error(`API request failed (${response.status})`);
      }

      const data: { response: string } = await response.json();

      setMessages((previous) => [
        ...previous,
        { role: "assistant", content: data.response },
      ]);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Something went wrong.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-4xl flex-col px-4 py-8">
      <header className="mb-8">
        <h1 className="text-2xl font-bold">AI Engineering Assistant</h1>
        <p className="mt-1 text-sm text-gray-500">
          Learn, explore, and solve engineering problems with AI.
        </p>
      </header>

      <section
        aria-live="polite"
        className="flex-1 space-y-6 pb-6"
      >
        {messages.length === 0 && (
          <div className="rounded-xl border border-dashed p-8 text-center">
            <Bot className="mx-auto mb-3" size={32} />
            <h2 className="font-semibold">What are you building today?</h2>
            <p className="mt-2 text-sm text-gray-500">
              Ask about LangChain, LangGraph, RAG, or AI architecture.
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <article key={index} className="flex gap-3">
            <div className="mt-1 shrink-0">
              {message.role === "user" ? (
                <User size={20} />
              ) : (
                <Bot size={20} />
              )}
            </div>

            <div className="min-w-0 flex-1">
              <p className="mb-2 text-sm font-semibold">
                {message.role === "user" ? "You" : "Assistant"}
              </p>
              {message.role === "assistant" ? (
                <div className="prose prose-sm max-w-none dark:prose-invert">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {message.content}
                  </ReactMarkdown>
                </div>
              ) : (
                <p className="whitespace-pre-wrap">{message.content}</p>
              )}
            </div>
          </article>
        ))}

        {loading && (
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <LoaderCircle className="animate-spin" size={18} />
            Generating response...
          </div>
        )}

        {error && (
          <p role="alert" className="text-sm text-red-600">
            {error}
          </p>
        )}
      </section>

      <form onSubmit={handleSubmit} className="sticky bottom-0 bg-background py-3">
        <div className="flex gap-2 rounded-xl border p-2 shadow-sm">
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask an engineering question..."
            aria-label="Your message"
            className="min-w-0 flex-1 bg-transparent px-3 outline-none"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            aria-label="Send message"
            className="rounded-lg bg-black p-3 text-white disabled:opacity-40"
          >
            <Send size={18} />
          </button>
        </div>
      </form>
    </main>
  );
}
