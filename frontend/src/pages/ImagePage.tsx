/**
 * NASA-Grade Image Generation Interface
 * Stable Diffusion XL Integration • 10X Speed
 */

import { useState, useCallback, memo } from 'react';
import { Image as ImageIcon, Download, Share2, Sparkles, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface ImagePageProps {
    mode: 'CLOUD' | 'LOCAL';
    backendUrl: string;
    health?: 'healthy' | 'degraded' | 'offline';
}

const ImagePage = memo(({ mode, backendUrl }: ImagePageProps) => {
    const [prompt, setPrompt] = useState('');
    const [generatedImage, setGeneratedImage] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleGenerate = useCallback(async (e: React.FormEvent) => {
        e.preventDefault();
        const activeUrl = backendUrl || 'https://ai-saas-backend-ds91.onrender.com';

        if (!prompt.trim() || loading) return;

        setLoading(true);
        setError(null);
        setGeneratedImage(null);

        try {
            // Usar URL absoluta para evitar problemas de proxy
            const response = await fetch(`${activeUrl}/image`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt,
                    model: "stable-diffusion-xl",
                    width: 1024,
                    height: 1024
                }),
            });

            if (!response.ok) throw new Error('Generation failed');

            const data = await response.json();
            const imageUrl = data.url || data.image_url || `data:image/png;base64,${data.image_base64}`;
            setGeneratedImage(imageUrl);
        } catch (err) {
            console.error(err);
            setError('Failed to generate image. Please try again.');
        } finally {
            setLoading(false);
        }
    }, [prompt, backendUrl]);

    return (
        <div className="h-full flex flex-col md:flex-row gap-6">
            {/* Controls Panel */}
            <div className="w-full md:w-1/3 space-y-6">
                <div>
                    <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                        Studio Nexus
                    </h2>
                    <p className="text-gray-400 text-sm mt-1">
                        Running on {mode === 'CLOUD' ? 'SDXL Cloud' : 'Local Stable Diffusion'}
                    </p>
                </div>

                <form onSubmit={handleGenerate} className="space-y-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-gray-300">Prompt Exploration</label>
                        <textarea
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                            placeholder="A futuristic city on Mars, neon lights, 8k resolution..."
                            className="w-full h-32 bg-gray-900/50 border border-gray-700 rounded-xl p-4 focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading || !prompt}
                        className={`w-full py-4 rounded-xl font-bold flex items-center justify-center space-x-2 transition-all ${loading
                            ? 'bg-gray-800 cursor-not-allowed'
                            : 'bg-gradient-to-r from-purple-500 to-pink-600 hover:shadow-lg hover:shadow-purple-500/25'
                            }`}
                    >
                        {loading ? (
                            <>
                                <Sparkles className="w-5 h-5 animate-spin" />
                                <span>Dreaming...</span>
                            </>
                        ) : (
                            <>
                                <ImageIcon className="w-5 h-5" />
                                <span>Generate Masterpiece</span>
                            </>
                        )}
                    </button>
                </form>

                {error && (
                    <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center space-x-3 text-red-400">
                        <AlertCircle className="w-5 h-5" />
                        <span className="text-sm">{error}</span>
                    </div>
                )}
            </div>

            {/* Preview Panel */}
            <div className="flex-1 rounded-2xl bg-gray-900/30 border border-gray-800/50 flex items-center justify-center p-8 relative overflow-hidden group">
                <div className="absolute inset-0 bg-cyber-grid opacity-20 pointer-events-none" />

                <AnimatePresence mode="wait">
                    {generatedImage ? (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.9 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="relative max-w-full max-h-full shadow-2xl rounded-lg overflow-hidden"
                        >
                            <img src={generatedImage} alt="Generated" className="max-w-full max-h-[600px] object-contain" />

                            <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex justify-center space-x-4">
                                <button className="p-2 bg-white/10 rounded-full hover:bg-white/20 backdrop-blur-sm">
                                    <Download className="w-5 h-5" />
                                </button>
                                <button className="p-2 bg-white/10 rounded-full hover:bg-white/20 backdrop-blur-sm">
                                    <Share2 className="w-5 h-5" />
                                </button>
                            </div>
                        </motion.div>
                    ) : (
                        <div className="text-center text-gray-600">
                            <ImageIcon className="w-16 h-16 mx-auto mb-4 opacity-50" />
                            <p>Your imagination is the limit</p>
                        </div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
});

ImagePage.displayName = 'ImagePage';
export default ImagePage;
