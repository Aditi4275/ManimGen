"use client";

import { useState, useEffect, useCallback } from "react";
import { useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import Link from "next/link";
import {
    Play,
    ArrowLeft,
    Download,
    Eye,
    EyeOff,
    Loader2,
    CheckCircle,
    AlertCircle,
    Film,
    Zap,
} from "lucide-react";

import { PromptInput } from "@/components/PromptInput";
import { VideoPreview } from "@/components/VideoPreview";
import { Timeline } from "@/components/Timeline";
import { CodeEditor } from "@/components/CodeEditor";
import { VoiceOver } from "@/components/VoiceOver";
import {
    projectsApi,
    scenesApi,
    renderApi,
    audioApi,
    getVideoUrl,
    type Project,
    type Scene,
} from "@/lib/api";

export function EditorContent() {
    const searchParams = useSearchParams();
    const initialPrompt = searchParams.get("prompt") || "";

    // State
    const [project, setProject] = useState<Project | null>(null);
    const [scenes, setScenes] = useState<Scene[]>([]);
    const [selectedScene, setSelectedScene] = useState<Scene | null>(null);
    const [isGenerating, setIsGenerating] = useState(false);
    const [isGeneratingMulti, setIsGeneratingMulti] = useState(false);
    const [isRendering, setIsRendering] = useState(false);
    const [isRenderingAll, setIsRenderingAll] = useState(false);
    const [renderAllProgress, setRenderAllProgress] = useState("");
    const [isExporting, setIsExporting] = useState(false);
    const [showCode, setShowCode] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [notification, setNotification] = useState<{
        type: "success" | "error";
        message: string;
    } | null>(null);

    // Initialize project
    useEffect(() => {
        const initProject = async () => {
            try {
                const response = await projectsApi.create("MotionScript");
                if (response.data) {
                    setProject(response.data);
                }
            } catch (err) {
                console.error("Failed to create project:", err);
                setError("Failed to initialize project. Please refresh the page.");
            }
        };

        initProject();
    }, []);

    // Handle initial prompt
    useEffect(() => {
        if (initialPrompt && project && scenes.length === 0) {
            handleGenerateScene(initialPrompt);
        }
    }, [initialPrompt, project]);

    const showNotification = (type: "success" | "error", message: string) => {
        setNotification({ type, message });
        setTimeout(() => setNotification(null), 3000);
    };

    // Generate scene from prompt
    const handleGenerateScene = useCallback(
        async (prompt: string) => {
            if (!project) return;

            setIsGenerating(true);
            setError(null);

            try {
                const response = await scenesApi.create(project.id, prompt);
                if (response.data) {
                    setScenes((prev) => [...prev, response.data!]);
                    setSelectedScene(response.data);
                    showNotification("success", "Scene created! Click Render to generate the video.");
                }
            } catch (err) {
                const message = err instanceof Error ? err.message : "Failed to generate scene";
                setError(message);
                showNotification("error", message);
            } finally {
                setIsGenerating(false);
            }
        },
        [project]
    );

    // Generate multiple scenes for 30-second video
    const handleGenerateMultiScenes = useCallback(
        async (prompt: string) => {
            if (!project) return;

            setIsGeneratingMulti(true);
            setError(null);

            try {
                const response = await scenesApi.createMulti(project.id, prompt, 5);
                if (response.data && Array.isArray(response.data)) {
                    setScenes((prev) => [...prev, ...response.data!]);
                    if (response.data.length > 0) {
                        setSelectedScene(response.data[0]);
                    }
                    showNotification("success", `Created ${response.data.length} scenes! Render each one, then Export.`);
                }
            } catch (err) {
                const message = err instanceof Error ? err.message : "Failed to generate scenes";
                setError(message);
                showNotification("error", message);
            } finally {
                setIsGeneratingMulti(false);
            }
        },
        [project]
    );

    // Render a scene
    const handleRenderScene = useCallback(async (sceneId: string) => {
        setIsRendering(true);

        try {
            const response = await renderApi.renderScene(sceneId);
            if (response.data) {
                // Poll for completion
                const pollStatus = async () => {
                    const statusResponse = await renderApi.getJobStatus(response.data!.id);
                    const job = statusResponse.data;

                    if (job?.status === "completed") {
                        // Update scene with video URL
                        setScenes((prev) =>
                            prev.map((s) =>
                                s.id === sceneId
                                    ? {
                                        ...s,
                                        status: "completed" as const,
                                        video_url: job.output_url,
                                    }
                                    : s
                            )
                        );
                        if (selectedScene?.id === sceneId) {
                            setSelectedScene((prev) =>
                                prev
                                    ? { ...prev, status: "completed", video_url: job.output_url }
                                    : null
                            );
                        }
                        showNotification("success", "Scene rendered successfully!");
                        setIsRendering(false);
                    } else if (job?.status === "failed") {
                        setScenes((prev) =>
                            prev.map((s) =>
                                s.id === sceneId
                                    ? { ...s, status: "failed" as const, error_message: job.error_message }
                                    : s
                            )
                        );
                        showNotification("error", job.error_message || "Render failed");
                        setIsRendering(false);
                    } else {
                        // Still rendering, poll again
                        setTimeout(pollStatus, 2000);
                    }
                };

                // Update scene status to rendering
                setScenes((prev) =>
                    prev.map((s) =>
                        s.id === sceneId ? { ...s, status: "rendering" as const } : s
                    )
                );

                pollStatus();
            }
        } catch (err) {
            const message = err instanceof Error ? err.message : "Failed to start render";
            showNotification("error", message);
            setIsRendering(false);
        }
    }, [selectedScene]);

    // Delete a scene
    const handleDeleteScene = useCallback(async (sceneId: string) => {
        try {
            await scenesApi.delete(sceneId);
            setScenes((prev) => prev.filter((s) => s.id !== sceneId));
            if (selectedScene?.id === sceneId) {
                setSelectedScene(null);
            }
            showNotification("success", "Scene deleted");
        } catch (err) {
            showNotification("error", "Failed to delete scene");
        }
    }, [selectedScene]);

    // Reorder scenes
    const handleReorderScenes = useCallback((newOrder: Scene[]) => {
        setScenes(newOrder);
        // Update order indices on backend
        newOrder.forEach((scene, index) => {
            if (scene.order_index !== index) {
                scenesApi.update(scene.id, { order_index: index });
            }
        });
    }, []);

    // Upload audio
    const handleAudioUpload = useCallback(
        async (file: File) => {
            if (!project) return;

            try {
                await audioApi.upload(project.id, file);
                setProject((prev) =>
                    prev ? { ...prev, audio_url: URL.createObjectURL(file) } : null
                );
                showNotification("success", "Audio uploaded successfully");
            } catch (err) {
                showNotification("error", "Failed to upload audio");
            }
        },
        [project]
    );

    // Delete audio
    const handleAudioDelete = useCallback(async () => {
        if (!project) return;

        try {
            await audioApi.delete(project.id);
            setProject((prev) => (prev ? { ...prev, audio_url: undefined } : null));
            showNotification("success", "Audio removed");
        } catch (err) {
            showNotification("error", "Failed to remove audio");
        }
    }, [project]);

    // Export project
    const handleExport = useCallback(async () => {
        if (!project) return;

        const completedScenes = scenes.filter((s) => s.status === "completed");
        if (completedScenes.length === 0) {
            showNotification("error", "No rendered scenes to export");
            return;
        }

        setIsExporting(true);

        try {
            const response = await renderApi.exportProject(project.id);
            if (response.data) {
                const pollStatus = async () => {
                    const statusResponse = await renderApi.getJobStatus(response.data!.id);
                    const job = statusResponse.data;

                    if (job?.status === "completed" && job.output_url) {
                        // Download the video
                        const link = document.createElement("a");
                        link.href = getVideoUrl(job.output_url);
                        link.download = `${project.name || "animation"}.mp4`;
                        link.click();
                        showNotification("success", "Export complete!");
                        setIsExporting(false);
                    } else if (job?.status === "failed") {
                        showNotification("error", job.error_message || "Export failed");
                        setIsExporting(false);
                    } else {
                        setTimeout(pollStatus, 2000);
                    }
                };

                pollStatus();
            }
        } catch (err) {
            showNotification("error", "Failed to export project");
            setIsExporting(false);
        }
    }, [project, scenes]);

    // Render all scenes and combine
    const handleRenderAllAndCombine = useCallback(async () => {
        if (!project || scenes.length === 0) return;

        setIsRenderingAll(true);
        setRenderAllProgress("Starting...");

        try {
            const response = await renderApi.renderAllAndCombine(project.id);
            if (response.data) {
                const pollStatus = async () => {
                    const statusResponse = await renderApi.getJobStatus(response.data!.id);
                    const job = statusResponse.data;

                    setRenderAllProgress(job?.status || "Processing...");

                    if (job?.status === "completed" && job.output_url) {
                        // Download the video
                        const link = document.createElement("a");
                        link.href = getVideoUrl(job.output_url);
                        link.download = `${project.name || "animation"}.mp4`;
                        link.click();
                        showNotification("success", "Video rendered and downloaded!");
                        setIsRenderingAll(false);
                        setRenderAllProgress("");

                        // Refresh scenes to get updated status
                        const scenesResponse = await scenesApi.list(project.id);
                        if (scenesResponse.data) {
                            setScenes(scenesResponse.data);
                        }
                    } else if (job?.status === "failed") {
                        showNotification("error", job.error_message || "Render failed");
                        setIsRenderingAll(false);
                        setRenderAllProgress("");
                    } else {
                        setTimeout(pollStatus, 2000);
                    }
                };

                pollStatus();
            }
        } catch (err) {
            showNotification("error", "Failed to render scenes");
            setIsRenderingAll(false);
            setRenderAllProgress("");
        }
    }, [project, scenes]);

    return (
        <div className="min-h-screen flex flex-col">
            {/* Header */}
            <header className="flex-shrink-0 border-b border-[var(--border)] bg-[var(--card)]">
                <div className="flex items-center justify-between px-4 py-3">
                    <div className="flex items-center gap-4">
                        <Link href="/" className="btn btn-ghost p-2">
                            <ArrowLeft className="w-5 h-5" />
                        </Link>
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-400 flex items-center justify-center">
                                <Play className="w-4 h-4 text-white" fill="white" />
                            </div>
                            <span className="font-semibold">{project?.name || "Loading..."}</span>
                        </div>
                    </div>

                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => setShowCode(!showCode)}
                            className={`btn ${showCode ? "btn-primary" : "btn-secondary"}`}
                        >
                            {showCode ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                            {showCode ? "Hide Code" : "Show Code"}
                        </button>
                        <button
                            onClick={handleExport}
                            disabled={isExporting || scenes.filter((s) => s.status === "completed").length === 0}
                            className="btn btn-primary"
                        >
                            {isExporting ? (
                                <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                                <Download className="w-4 h-4" />
                            )}
                            Export Video
                        </button>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <div className="flex-1 flex overflow-hidden">
                {/* Left Panel - Prompt & Scenes */}
                <div className="w-96 flex-shrink-0 border-r border-[var(--border)] p-4 overflow-y-auto">
                    <div className="space-y-6">
                        <div>
                            <h2 className="text-lg font-semibold mb-3">Create Scene</h2>
                            <PromptInput
                                onSubmit={handleGenerateScene}
                                isLoading={isGenerating || isGeneratingMulti}
                                disabled={!project}
                            />
                            <button
                                onClick={() => {
                                    const prompt = (document.querySelector('textarea') as HTMLTextAreaElement)?.value || 'Create an animation';
                                    handleGenerateMultiScenes(prompt);
                                }}
                                disabled={!project || isGeneratingMulti || isGenerating}
                                className="btn btn-secondary w-full mt-2"
                            >
                                {isGeneratingMulti ? (
                                    <>
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                        Generating...
                                    </>
                                ) : (
                                    <>
                                        <Film className="w-4 h-4" />
                                        Generate 30s Video (5 Scenes)
                                    </>
                                )}
                            </button>
                            {scenes.length > 1 && (
                                <button
                                    onClick={handleRenderAllAndCombine}
                                    disabled={!project || isRenderingAll || scenes.length === 0}
                                    className="btn btn-primary w-full mt-2"
                                >
                                    {isRenderingAll ? (
                                        <>
                                            <Loader2 className="w-4 h-4 animate-spin" />
                                            {renderAllProgress || "Rendering..."}
                                        </>
                                    ) : (
                                        <>
                                            <Zap className="w-4 h-4" />
                                            Render All & Download
                                        </>
                                    )}
                                </button>
                            )}
                        </div>

                        {error && (
                            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
                                <div className="flex items-center gap-2">
                                    <AlertCircle className="w-4 h-4" />
                                    {error}
                                </div>
                            </div>
                        )}

                        <VoiceOver
                            audioUrl={project?.audio_url}
                            onUpload={handleAudioUpload}
                            onDelete={handleAudioDelete}
                        />
                    </div>
                </div>

                {/* Center - Preview & Code */}
                <div className="flex-1 flex flex-col overflow-hidden">
                    <div className="flex-1 p-4 overflow-y-auto">
                        <div className="max-w-4xl mx-auto space-y-4">
                            <VideoPreview
                                videoUrl={selectedScene?.video_url}
                                thumbnailUrl={selectedScene?.thumbnail_url}
                                isLoading={isRendering && selectedScene?.status === "rendering"}
                                onRegenerate={
                                    selectedScene
                                        ? () => scenesApi.regenerate(selectedScene.id)
                                        : undefined
                                }
                            />

                            {showCode && selectedScene?.code && (
                                <motion.div
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                >
                                    <CodeEditor
                                        code={selectedScene.code}
                                        readOnly={false}
                                        onChange={(newCode) => {
                                            scenesApi.update(selectedScene.id, { code: newCode });
                                            setSelectedScene((prev) =>
                                                prev ? { ...prev, code: newCode } : null
                                            );
                                        }}
                                        onRun={() => handleRenderScene(selectedScene.id)}
                                        isRunning={isRendering}
                                    />
                                </motion.div>
                            )}
                        </div>
                    </div>

                    {/* Timeline */}
                    <div className="flex-shrink-0 border-t border-[var(--border)] p-4 bg-[var(--card)]">
                        <Timeline
                            scenes={scenes}
                            onReorder={handleReorderScenes}
                            onSelectScene={setSelectedScene}
                            onDeleteScene={handleDeleteScene}
                            onRenderScene={handleRenderScene}
                            selectedSceneId={selectedScene?.id}
                        />
                    </div>
                </div>
            </div>

            {/* Notification Toast */}
            {notification && (
                <motion.div
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 50 }}
                    className={`fixed bottom-6 right-6 p-4 rounded-lg shadow-lg flex items-center gap-3 ${notification.type === "success"
                        ? "bg-green-500/90 text-white"
                        : "bg-red-500/90 text-white"
                        }`}
                >
                    {notification.type === "success" ? (
                        <CheckCircle className="w-5 h-5" />
                    ) : (
                        <AlertCircle className="w-5 h-5" />
                    )}
                    {notification.message}
                </motion.div>
            )}
        </div>
    );
}
