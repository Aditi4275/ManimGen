"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Code, Copy, Check, Edit3, Play, Loader2 } from "lucide-react";

interface CodeEditorProps {
    code: string;
    onChange?: (code: string) => void;
    onRun?: (code: string) => void;
    readOnly?: boolean;
    isRunning?: boolean;
}

export function CodeEditor({
    code,
    onChange,
    onRun,
    readOnly = true,
    isRunning = false,
}: CodeEditorProps) {
    const [isEditing, setIsEditing] = useState(false);
    const [editedCode, setEditedCode] = useState(code);
    const [copied, setCopied] = useState(false);
    const [lineNumbers, setLineNumbers] = useState<number[]>([]);

    useEffect(() => {
        setEditedCode(code);
        const lines = code.split("\n").length;
        setLineNumbers(Array.from({ length: lines }, (_, i) => i + 1));
    }, [code]);

    const handleCopy = async () => {
        await navigator.clipboard.writeText(code);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const handleSave = () => {
        if (onChange) {
            onChange(editedCode);
        }
        setIsEditing(false);
    };

    const handleCancel = () => {
        setEditedCode(code);
        setIsEditing(false);
    };

    // Simple syntax highlighting
    const highlightCode = (code: string) => {
        return code
            .replace(/\b(from|import|class|def|return|if|else|for|while|in|and|or|not|True|False|None|self)\b/g, '<span class="text-purple-400">$1</span>')
            .replace(/\b(Circle|Square|Rectangle|Arrow|Text|MathTex|VGroup|Scene|Create|Write|Transform|FadeIn|FadeOut|GrowArrow)\b/g, '<span class="text-cyan-400">$1</span>')
            .replace(/(#.*$)/gm, '<span class="text-green-500">$1</span>')
            .replace(/(".*?"|'.*?')/g, '<span class="text-amber-400">$1</span>')
            .replace(/\b(\d+\.?\d*)\b/g, '<span class="text-orange-400">$1</span>');
    };

    return (
        <div className="card">
            <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                    <Code className="w-4 h-4 text-[var(--primary)]" />
                    <h3 className="font-semibold text-sm">Generated Code</h3>
                </div>
                <div className="flex items-center gap-2">
                    {!readOnly && !isEditing && (
                        <button
                            onClick={() => setIsEditing(true)}
                            className="btn btn-ghost text-xs py-1 px-2"
                        >
                            <Edit3 className="w-3 h-3" />
                            Edit
                        </button>
                    )}
                    {isEditing && (
                        <>
                            <button
                                onClick={handleCancel}
                                className="btn btn-ghost text-xs py-1 px-2"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleSave}
                                className="btn btn-primary text-xs py-1 px-2"
                            >
                                Save
                            </button>
                        </>
                    )}
                    <button
                        onClick={handleCopy}
                        className="btn btn-ghost text-xs py-1 px-2"
                    >
                        {copied ? (
                            <Check className="w-3 h-3 text-green-400" />
                        ) : (
                            <Copy className="w-3 h-3" />
                        )}
                    </button>
                    {onRun && (
                        <button
                            onClick={() => onRun(isEditing ? editedCode : code)}
                            disabled={isRunning}
                            className="btn btn-primary text-xs py-1 px-2"
                        >
                            {isRunning ? (
                                <Loader2 className="w-3 h-3 animate-spin" />
                            ) : (
                                <Play className="w-3 h-3" />
                            )}
                            Run
                        </button>
                    )}
                </div>
            </div>

            <div className="relative bg-[var(--secondary)] rounded-lg overflow-hidden">
                <div className="flex max-h-[400px] overflow-auto">
                    {/* Line numbers */}
                    <div className="flex-shrink-0 py-3 px-3 text-right text-xs text-[var(--muted)] select-none border-r border-[var(--border)] bg-[var(--secondary)]">
                        {lineNumbers.map((num) => (
                            <div key={num} className="leading-5">
                                {num}
                            </div>
                        ))}
                    </div>

                    {/* Code content */}
                    <div className="flex-1 overflow-x-auto">
                        {isEditing ? (
                            <textarea
                                value={editedCode}
                                onChange={(e) => setEditedCode(e.target.value)}
                                className="w-full min-w-[600px] p-3 bg-transparent text-sm font-mono leading-5 resize-none focus:outline-none"
                                style={{ minHeight: `${lineNumbers.length * 20 + 24}px` }}
                                spellCheck={false}
                            />
                        ) : (
                            <pre className="p-3 text-sm font-mono leading-5 min-w-[600px]">
                                <code
                                    dangerouslySetInnerHTML={{
                                        __html: highlightCode(code),
                                    }}
                                />
                            </pre>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
