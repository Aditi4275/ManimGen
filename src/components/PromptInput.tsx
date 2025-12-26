"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Loader2, Sparkles, Lightbulb } from "lucide-react";

interface PromptInputProps {
    onSubmit: (prompt: string) => Promise<void>;
    isLoading?: boolean;
    disabled?: boolean;
}

const suggestionPrompts = [
    "Create a circle that transforms into a square",
    "Show the Pythagorean theorem with animated proof",
    "Visualize binary search on a sorted array",
    "Animate data flow from client to server to database",
];

export function PromptInput({ onSubmit, isLoading = false, disabled = false }: PromptInputProps) {
    const [prompt, setPrompt] = useState("");
    const [showSuggestions, setShowSuggestions] = useState(true);

    const handleSubmit = useCallback(async () => {
        if (!prompt.trim() || isLoading || disabled) return;
        await onSubmit(prompt.trim());
        setPrompt("");
        setShowSuggestions(false);
    }, [prompt, isLoading, disabled, onSubmit]);

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
        }
    };

    const handleSuggestionClick = (suggestion: string) => {
        setPrompt(suggestion);
        setShowSuggestions(false);
    };

    const charCount = prompt.length;
    const maxChars = 500;

    return (
        <div className="space-y-4">
            <div className="relative">
                <div className="card p-0 overflow-hidden">
                    <textarea
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value.slice(0, maxChars))}
                        onKeyDown={handleKeyDown}
                        placeholder="Describe the animation you want to create..."
                        disabled={isLoading || disabled}
                        className="w-full p-4 pr-24 bg-transparent border-none resize-none focus:outline-none focus:ring-0 min-h-[100px]"
                        rows={3}
                    />
                    <div className="absolute bottom-3 right-3 flex items-center gap-3">
                        <span className="text-xs text-[var(--muted)]">
                            {charCount}/{maxChars}
                        </span>
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={handleSubmit}
                            disabled={!prompt.trim() || isLoading || disabled}
                            className="btn btn-primary h-10 w-10 p-0 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {isLoading ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <Send className="w-5 h-5" />
                            )}
                        </motion.button>
                    </div>
                </div>
            </div>

            <AnimatePresence>
                {showSuggestions && !prompt && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="space-y-2"
                    >
                        <div className="flex items-center gap-2 text-sm text-[var(--muted)]">
                            <Lightbulb className="w-4 h-4" />
                            <span>Try one of these:</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                            {suggestionPrompts.map((suggestion, index) => (
                                <motion.button
                                    key={index}
                                    initial={{ opacity: 0, scale: 0.9 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: index * 0.05 }}
                                    onClick={() => handleSuggestionClick(suggestion)}
                                    className="px-3 py-1.5 text-sm rounded-full bg-[var(--secondary)] border border-[var(--border)] hover:border-[var(--primary)] hover:bg-[var(--primary)]/10 transition-all"
                                >
                                    {suggestion}
                                </motion.button>
                            ))}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {isLoading && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex items-center gap-2 text-sm text-[var(--primary)]"
                >
                    <Sparkles className="w-4 h-4 animate-pulse" />
                    <span>Generating Manim code...</span>
                </motion.div>
            )}
        </div>
    );
}
