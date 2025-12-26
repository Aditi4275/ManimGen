const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Types
export interface Project {
    id: string;
    name: string;
    description?: string;
    created_at: string;
    updated_at: string;
    scene_count: number;
    audio_url?: string;
}

export interface Scene {
    id: string;
    project_id: string;
    prompt: string;
    code?: string;
    video_url?: string;
    thumbnail_url?: string;
    duration_seconds: number;
    order_index: number;
    status: 'pending' | 'generating' | 'rendering' | 'completed' | 'failed';
    error_message?: string;
    created_at: string;
    updated_at: string;
}

export interface RenderJob {
    id: string;
    scene_id?: string;
    project_id?: string;
    status: string;
    progress: number;
    output_url?: string;
    error_message?: string;
    created_at: string;
}

interface ApiResponse<T> {
    success: boolean;
    data?: T;
    message?: string;
}

// API Helper
async function fetchApi<T>(
    endpoint: string,
    options?: RequestInit
): Promise<ApiResponse<T>> {
    const response = await fetch(`${API_BASE_URL}/api${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options?.headers,
        },
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
}

// Projects API
export const projectsApi = {
    create: async (name: string, description?: string) => {
        return fetchApi<Project>('/projects/', {
            method: 'POST',
            body: JSON.stringify({ name, description }),
        });
    },

    list: async () => {
        return fetchApi<Project[]>('/projects/');
    },

    get: async (id: string) => {
        return fetchApi<Project>(`/projects/${id}`);
    },

    update: async (id: string, data: { name?: string; description?: string }) => {
        return fetchApi<Project>(`/projects/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    delete: async (id: string) => {
        return fetchApi<void>(`/projects/${id}`, {
            method: 'DELETE',
        });
    },
};

// Scenes API
export const scenesApi = {
    create: async (projectId: string, prompt: string) => {
        return fetchApi<Scene>('/scenes/', {
            method: 'POST',
            body: JSON.stringify({ project_id: projectId, prompt }),
        });
    },

    createMulti: async (projectId: string, prompt: string, numScenes: number = 5) => {
        return fetchApi<Scene[]>('/scenes/multi', {
            method: 'POST',
            body: JSON.stringify({ project_id: projectId, prompt, num_scenes: numScenes }),
        });
    },

    list: async (projectId: string) => {
        return fetchApi<Scene[]>(`/scenes/project/${projectId}`);
    },

    get: async (id: string) => {
        return fetchApi<Scene>(`/scenes/${id}`);
    },

    update: async (id: string, data: { prompt?: string; code?: string; order_index?: number }) => {
        return fetchApi<Scene>(`/scenes/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    delete: async (id: string) => {
        return fetchApi<void>(`/scenes/${id}`, {
            method: 'DELETE',
        });
    },

    regenerate: async (id: string, newPrompt?: string) => {
        const url = newPrompt ? `/scenes/${id}/regenerate?new_prompt=${encodeURIComponent(newPrompt)}` : `/scenes/${id}/regenerate`;
        return fetchApi<Scene>(url, {
            method: 'POST',
        });
    },
};

// Render API
export const renderApi = {
    renderScene: async (sceneId: string) => {
        return fetchApi<RenderJob>(`/render/scene/${sceneId}`, {
            method: 'POST',
        });
    },

    getJobStatus: async (jobId: string) => {
        return fetchApi<RenderJob>(`/render/job/${jobId}`);
    },

    exportProject: async (projectId: string) => {
        return fetchApi<RenderJob>(`/render/export/${projectId}`, {
            method: 'POST',
        });
    },

    renderAllAndCombine: async (projectId: string) => {
        return fetchApi<RenderJob>(`/render/render-all/${projectId}`, {
            method: 'POST',
        });
    },
};

// Audio API
export const audioApi = {
    upload: async (projectId: string, file: File) => {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/api/audio/upload/${projectId}`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Upload failed' }));
            throw new Error(error.detail);
        }

        return response.json();
    },

    delete: async (projectId: string) => {
        return fetchApi<void>(`/audio/${projectId}`, {
            method: 'DELETE',
        });
    },
};

// Video URL helper
export function getVideoUrl(path: string): string {
    if (path.startsWith('http')) return path;
    return `${API_BASE_URL}${path}`;
}
