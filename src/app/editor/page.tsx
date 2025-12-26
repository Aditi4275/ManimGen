"use client";

import { Suspense } from "react";
import { EditorContent } from "./EditorContent";
import { Loader2 } from "lucide-react";

function EditorLoading() {
    return (
        <div className="min-h-screen flex items-center justify-center">
            <div className="text-center">
                <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-[var(--primary)]" />
                <p className="text-[var(--muted)]">Loading editor...</p>
            </div>
        </div>
    );
}

export default function EditorPage() {
    return (
        <Suspense fallback={<EditorLoading />}>
            <EditorContent />
        </Suspense>
    );
}
