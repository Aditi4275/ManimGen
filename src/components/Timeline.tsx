"use client";

import { useState } from "react";
import { motion, Reorder } from "framer-motion";
import { GripVertical, Play, Trash2, RotateCcw, Clock, AlertCircle } from "lucide-react";
import type { Scene } from "@/lib/api";
import { getVideoUrl } from "@/lib/api";

interface TimelineProps {
    scenes: Scene[];
    onReorder: (scenes: Scene[]) => void;
    onSelectScene: (scene: Scene) => void;
    onDeleteScene: (sceneId: string) => void;
    onRenderScene: (sceneId: string) => void;
    selectedSceneId?: string;
}

export function Timeline({
    scenes,
    onReorder,
    onSelectScene,
    onDeleteScene,
    onRenderScene,
    selectedSceneId,
}: TimelineProps) {
    const getStatusBadge = (status: Scene["status"]) => {
        switch (status) {
            case "completed":
                return <span className="badge badge-success">Ready</span>;
            case "rendering":
                return <span className="badge badge-warning">Rendering</span>;
            case "generating":
                return <span className="badge badge-pending">Generating</span>;
            case "failed":
                return <span className="badge badge-error">Failed</span>;
            default:
                return <span className="badge badge-pending">Pending</span>;
        }
    };

    const formatDuration = (seconds: number) => {
        if (!seconds) return "0:00";
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, "0")}`;
    };

    const totalDuration = scenes.reduce((acc, scene) => acc + (scene.duration_seconds || 0), 0);

    return (
        <div className="card">
            <div className="flex items-center justify-between mb-4">
                <h3 className="font-semibold">Timeline</h3>
                <div className="flex items-center gap-2 text-sm text-[var(--muted)]">
                    <Clock className="w-4 h-4" />
                    <span>Total: {formatDuration(totalDuration)}</span>
                </div>
            </div>

            {scenes.length === 0 ? (
                <div className="timeline-track flex items-center justify-center text-[var(--muted)] text-sm">
                    No scenes yet. Create your first scene above!
                </div>
            ) : (
                <Reorder.Group
                    axis="x"
                    values={scenes}
                    onReorder={onReorder}
                    className="flex gap-3 overflow-x-auto pb-2"
                >
                    {scenes.map((scene, index) => (
                        <Reorder.Item
                            key={scene.id}
                            value={scene}
                            className={`timeline-item flex-shrink-0 w-48 p-3 ${selectedSceneId === scene.id ? "border-[var(--primary)]" : ""
                                }`}
                            onClick={() => onSelectScene(scene)}
                        >
                            <div className="flex items-center gap-2 mb-2">
                                <GripVertical className="w-4 h-4 text-[var(--muted)] cursor-grab" />
                                <span className="text-xs font-medium text-[var(--muted)]">
                                    Scene {index + 1}
                                </span>
                            </div>

                            {/* Thumbnail */}
                            <div className="aspect-video bg-[var(--secondary)] rounded-lg mb-2 overflow-hidden relative">
                                {scene.thumbnail_url ? (
                                    <img
                                        src={getVideoUrl(scene.thumbnail_url)}
                                        alt={`Scene ${index + 1}`}
                                        className="w-full h-full object-cover"
                                    />
                                ) : scene.status === "completed" && scene.video_url ? (
                                    <div className="w-full h-full flex items-center justify-center">
                                        <Play className="w-6 h-6 text-[var(--muted)]" />
                                    </div>
                                ) : (
                                    <div className="w-full h-full skeleton" />
                                )}

                                {scene.status === "failed" && (
                                    <div className="absolute inset-0 bg-red-500/20 flex items-center justify-center">
                                        <AlertCircle className="w-6 h-6 text-red-500" />
                                    </div>
                                )}
                            </div>

                            {/* Info */}
                            <div className="space-y-2">
                                <p className="text-xs text-[var(--muted)] line-clamp-2">
                                    {scene.prompt}
                                </p>
                                <div className="flex items-center justify-between">
                                    {getStatusBadge(scene.status)}
                                    <span className="text-xs text-[var(--muted)]">
                                        {formatDuration(scene.duration_seconds)}
                                    </span>
                                </div>
                            </div>

                            {/* Actions */}
                            <div className="flex items-center gap-1 mt-2 pt-2 border-t border-[var(--border)]">
                                {scene.status === "pending" && (
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onRenderScene(scene.id);
                                        }}
                                        className="flex-1 btn btn-primary text-xs py-1.5"
                                    >
                                        <Play className="w-3 h-3" />
                                        Render
                                    </button>
                                )}
                                {scene.status === "failed" && (
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onRenderScene(scene.id);
                                        }}
                                        className="flex-1 btn btn-secondary text-xs py-1.5"
                                    >
                                        <RotateCcw className="w-3 h-3" />
                                        Retry
                                    </button>
                                )}
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        onDeleteScene(scene.id);
                                    }}
                                    className="btn btn-ghost text-xs py-1.5 px-2 text-red-400 hover:bg-red-500/10"
                                >
                                    <Trash2 className="w-3 h-3" />
                                </button>
                            </div>
                        </Reorder.Item>
                    ))}
                </Reorder.Group>
            )}
        </div>
    );
}
