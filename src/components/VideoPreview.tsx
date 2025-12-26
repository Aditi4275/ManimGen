"use client";

import { useRef, useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Play, Pause, Maximize2, Volume2, VolumeX, RotateCcw } from "lucide-react";
import { getVideoUrl } from "@/lib/api";

interface VideoPreviewProps {
    videoUrl?: string;
    thumbnailUrl?: string;
    isLoading?: boolean;
    onRegenerate?: () => void;
}

export function VideoPreview({
    videoUrl,
    thumbnailUrl,
    isLoading = false,
    onRegenerate,
}: VideoPreviewProps) {
    const videoRef = useRef<HTMLVideoElement>(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [isMuted, setIsMuted] = useState(false);
    const [progress, setProgress] = useState(0);
    const [duration, setDuration] = useState(0);

    useEffect(() => {
        const video = videoRef.current;
        if (!video) return;

        const handleTimeUpdate = () => {
            setProgress((video.currentTime / video.duration) * 100);
        };

        const handleLoadedMetadata = () => {
            setDuration(video.duration);
        };

        const handleEnded = () => {
            setIsPlaying(false);
        };

        video.addEventListener("timeupdate", handleTimeUpdate);
        video.addEventListener("loadedmetadata", handleLoadedMetadata);
        video.addEventListener("ended", handleEnded);

        return () => {
            video.removeEventListener("timeupdate", handleTimeUpdate);
            video.removeEventListener("loadedmetadata", handleLoadedMetadata);
            video.removeEventListener("ended", handleEnded);
        };
    }, [videoUrl]);

    const togglePlay = () => {
        if (!videoRef.current) return;
        if (isPlaying) {
            videoRef.current.pause();
        } else {
            videoRef.current.play();
        }
        setIsPlaying(!isPlaying);
    };

    const toggleMute = () => {
        if (!videoRef.current) return;
        videoRef.current.muted = !isMuted;
        setIsMuted(!isMuted);
    };

    const handleFullscreen = () => {
        if (!videoRef.current) return;
        videoRef.current.requestFullscreen();
    };

    const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!videoRef.current) return;
        const rect = e.currentTarget.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const percentage = clickX / rect.width;
        videoRef.current.currentTime = percentage * duration;
    };

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, "0")}`;
    };

    return (
        <div className="card p-0 overflow-hidden">
            <div className="video-container relative group">
                {isLoading ? (
                    <div className="flex flex-col items-center justify-center p-8">
                        <div className="loader mb-4" />
                        <p className="text-[var(--muted)] text-sm">Rendering animation...</p>
                    </div>
                ) : videoUrl ? (
                    <>
                        <video
                            ref={videoRef}
                            src={getVideoUrl(videoUrl)}
                            poster={thumbnailUrl ? getVideoUrl(thumbnailUrl) : undefined}
                            className="w-full h-full object-contain"
                            onClick={togglePlay}
                        />

                        {/* Play overlay */}
                        {!isPlaying && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="absolute inset-0 flex items-center justify-center bg-black/30 cursor-pointer"
                                onClick={togglePlay}
                            >
                                <div className="w-16 h-16 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                                    <Play className="w-8 h-8 text-white" fill="white" />
                                </div>
                            </motion.div>
                        )}

                        {/* Controls */}
                        <div className="absolute bottom-0 left-0 right-0 p-3 bg-gradient-to-t from-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity">
                            {/* Progress bar */}
                            <div
                                className="h-1 bg-white/30 rounded-full mb-3 cursor-pointer"
                                onClick={handleProgressClick}
                            >
                                <div
                                    className="h-full bg-[var(--primary)] rounded-full transition-all"
                                    style={{ width: `${progress}%` }}
                                />
                            </div>

                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={togglePlay}
                                        className="p-1.5 rounded-lg hover:bg-white/20 transition-colors"
                                    >
                                        {isPlaying ? (
                                            <Pause className="w-5 h-5 text-white" />
                                        ) : (
                                            <Play className="w-5 h-5 text-white" fill="white" />
                                        )}
                                    </button>
                                    <button
                                        onClick={toggleMute}
                                        className="p-1.5 rounded-lg hover:bg-white/20 transition-colors"
                                    >
                                        {isMuted ? (
                                            <VolumeX className="w-5 h-5 text-white" />
                                        ) : (
                                            <Volume2 className="w-5 h-5 text-white" />
                                        )}
                                    </button>
                                    <span className="text-xs text-white/80">
                                        {formatTime(videoRef.current?.currentTime || 0)} / {formatTime(duration)}
                                    </span>
                                </div>

                                <div className="flex items-center gap-2">
                                    {onRegenerate && (
                                        <button
                                            onClick={onRegenerate}
                                            className="p-1.5 rounded-lg hover:bg-white/20 transition-colors"
                                            title="Regenerate"
                                        >
                                            <RotateCcw className="w-5 h-5 text-white" />
                                        </button>
                                    )}
                                    <button
                                        onClick={handleFullscreen}
                                        className="p-1.5 rounded-lg hover:bg-white/20 transition-colors"
                                    >
                                        <Maximize2 className="w-5 h-5 text-white" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </>
                ) : (
                    <div className="flex flex-col items-center justify-center p-8 text-center">
                        <div className="w-16 h-16 rounded-full bg-[var(--secondary)] flex items-center justify-center mb-4">
                            <Play className="w-8 h-8 text-[var(--muted)]" />
                        </div>
                        <p className="text-[var(--muted)]">
                            Enter a prompt to generate your first animation
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
}
