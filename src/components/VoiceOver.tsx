"use client";

import { useState, useRef } from "react";
import { motion } from "framer-motion";
import { Mic, Upload, Trash2, Play, Pause, Volume2 } from "lucide-react";

interface VoiceOverProps {
    audioUrl?: string;
    onUpload: (file: File) => Promise<void>;
    onDelete: () => void;
    isUploading?: boolean;
}

export function VoiceOver({
    audioUrl,
    onUpload,
    onDelete,
    isUploading = false,
}: VoiceOverProps) {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const audioRef = useRef<HTMLAudioElement>(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [progress, setProgress] = useState(0);
    const [duration, setDuration] = useState(0);

    const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        const validTypes = ["audio/mpeg", "audio/wav", "audio/mp3"];
        if (!validTypes.includes(file.type)) {
            alert("Please upload an MP3 or WAV file");
            return;
        }

        await onUpload(file);
        e.target.value = "";
    };

    const togglePlay = () => {
        if (!audioRef.current) return;
        if (isPlaying) {
            audioRef.current.pause();
        } else {
            audioRef.current.play();
        }
        setIsPlaying(!isPlaying);
    };

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, "0")}`;
    };

    return (
        <div className="card">
            <div className="flex items-center gap-2 mb-4">
                <Mic className="w-4 h-4 text-[var(--primary)]" />
                <h3 className="font-semibold text-sm">Voice-Over</h3>
            </div>

            {audioUrl ? (
                <div className="space-y-3">
                    <audio
                        ref={audioRef}
                        src={audioUrl}
                        onTimeUpdate={() => {
                            if (audioRef.current) {
                                setProgress((audioRef.current.currentTime / audioRef.current.duration) * 100);
                            }
                        }}
                        onLoadedMetadata={() => {
                            if (audioRef.current) {
                                setDuration(audioRef.current.duration);
                            }
                        }}
                        onEnded={() => setIsPlaying(false)}
                    />

                    {/* Waveform placeholder */}
                    <div className="h-16 bg-[var(--secondary)] rounded-lg flex items-center px-4">
                        <div className="w-full flex items-center gap-0.5">
                            {Array.from({ length: 50 }).map((_, i) => (
                                <div
                                    key={i}
                                    className="flex-1 bg-[var(--primary)] rounded-full transition-all"
                                    style={{
                                        height: `${Math.random() * 100}%`,
                                        opacity: progress > (i / 50) * 100 ? 1 : 0.3,
                                    }}
                                />
                            ))}
                        </div>
                    </div>

                    {/* Controls */}
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <button
                                onClick={togglePlay}
                                className="btn btn-secondary p-2"
                            >
                                {isPlaying ? (
                                    <Pause className="w-4 h-4" />
                                ) : (
                                    <Play className="w-4 h-4" fill="currentColor" />
                                )}
                            </button>
                            <span className="text-sm text-[var(--muted)]">
                                {formatTime(audioRef.current?.currentTime || 0)} / {formatTime(duration)}
                            </span>
                        </div>
                        <button
                            onClick={onDelete}
                            className="btn btn-ghost text-red-400 hover:bg-red-500/10"
                        >
                            <Trash2 className="w-4 h-4" />
                            Remove
                        </button>
                    </div>
                </div>
            ) : (
                <div className="space-y-3">
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept="audio/mpeg,audio/wav,audio/mp3"
                        onChange={handleFileSelect}
                        className="hidden"
                    />

                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => fileInputRef.current?.click()}
                        disabled={isUploading}
                        className="w-full p-6 border-2 border-dashed border-[var(--border)] rounded-xl hover:border-[var(--primary)] hover:bg-[var(--primary)]/5 transition-all"
                    >
                        <div className="flex flex-col items-center gap-2">
                            {isUploading ? (
                                <>
                                    <div className="loader" />
                                    <span className="text-sm text-[var(--muted)]">Uploading...</span>
                                </>
                            ) : (
                                <>
                                    <Upload className="w-8 h-8 text-[var(--muted)]" />
                                    <span className="text-sm text-[var(--muted)]">
                                        Upload audio file (MP3, WAV)
                                    </span>
                                </>
                            )}
                        </div>
                    </motion.button>

                    <p className="text-xs text-center text-[var(--muted)]">
                        Add narration to your animation. The audio will be synced with the final export.
                    </p>
                </div>
            )}
        </div>
    );
}
