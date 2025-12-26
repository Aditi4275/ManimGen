"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { Play, Sparkles, Layers, Mic, Code, ArrowRight } from "lucide-react";

const features = [
  {
    icon: Sparkles,
    title: "AI-Powered Generation",
    description: "Describe your animation in plain English and watch AI transform it into professional Manim code.",
  },
  {
    icon: Layers,
    title: "Scene-Based Editing",
    description: "Build complex videos by creating and arranging individual scenes on an intuitive timeline.",
  },
  {
    icon: Mic,
    title: "Voice-Over Integration",
    description: "Add narration to your animations with audio upload or text-to-speech generation.",
  },
  {
    icon: Code,
    title: "Code Visibility",
    description: "View and edit the generated Python code for full control over your animations.",
  },
];

const examples = [
  "Visualize a bubble sort algorithm step by step",
  "Show how a neural network processes an image",
  "Animate the Pythagorean theorem proof",
  "Create a client-server request flow diagram",
];

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-cyan-400 flex items-center justify-center">
              <Play className="w-4 h-4 text-white" fill="white" />
            </div>
            <span className="text-xl font-bold">MotionScript</span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/editor" className="btn btn-primary">
              Get Started
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              Transform Text into
              <br />
              <span className="gradient-text">Mathematical Animations</span>
            </h1>
            <p className="text-xl text-[var(--muted)] max-w-2xl mx-auto mb-10">
              Create stunning 3Blue1Brown-style educational videos using AI.
              Just describe what you want to animate, and let our AI generate the Manim code.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="flex flex-col sm:flex-row gap-4 justify-center mb-16"
          >
            <Link href="/editor" className="btn btn-primary text-lg px-8 py-4">
              <Sparkles className="w-5 h-5" />
              Start Creating
            </Link>
          </motion.div>

          {/* Animated Demo Preview */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="relative max-w-4xl mx-auto"
          >
            <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/20 to-cyan-500/20 blur-3xl -z-10" />
            <div className="card p-2">
              <div className="video-container bg-gradient-to-br from-indigo-900/50 to-purple-900/50">
                <div className="text-center p-8">
                  <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center animate-pulse-glow">
                    <Play className="w-8 h-8 text-white" fill="white" />
                  </div>
                  <p className="text-[var(--muted)]">Your generated animation will appear here</p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Example Prompts */}
      <section className="py-16 px-6 bg-[var(--secondary)]">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl font-semibold text-center mb-8">Try these prompts</h2>
          <div className="flex flex-wrap gap-3 justify-center">
            {examples.map((example, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: index * 0.1 }}
              >
                <Link
                  href={`/editor?prompt=${encodeURIComponent(example)}`}
                  className="inline-block px-4 py-2 rounded-full bg-[var(--card)] border border-[var(--border)] text-sm hover:border-[var(--primary)] hover:bg-[var(--primary)]/10 transition-all"
                >
                  &ldquo;{example}&rdquo;
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-4">
            Everything you need to create
            <br />
            <span className="gradient-text">educational animations</span>
          </h2>
          <p className="text-[var(--muted)] text-center max-w-2xl mx-auto mb-16">
            Our platform combines the power of AI with the precision of Manim
            to help you create professional-quality animations.
          </p>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="card card-hover"
              >
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center mb-4">
                  <feature.icon className="w-6 h-6 text-[var(--primary)]" />
                </div>
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-sm text-[var(--muted)]">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section className="py-20 px-6 bg-[var(--secondary)]">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
            How it works
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: "1", title: "Describe", desc: "Write a natural language description of the animation you want to create." },
              { step: "2", title: "Generate", desc: "Our AI generates Manim code and renders your animation in seconds." },
              { step: "3", title: "Export", desc: "Arrange scenes on the timeline, add voice-over, and export your video." },
            ].map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.15 }}
                viewport={{ once: true }}
                className="text-center"
              >
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-2xl font-bold">
                  {item.step}
                </div>
                <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                <p className="text-[var(--muted)]">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to create your first animation?
          </h2>
          <p className="text-[var(--muted)] mb-8">
            Join thousands of educators and content creators using MotionScript to bring their ideas to life.
          </p>
          <Link href="/editor" className="btn btn-primary text-lg px-8 py-4">
            <Sparkles className="w-5 h-5" />
            Start Creating for Free
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-[var(--border)]">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-gradient-to-br from-indigo-500 to-cyan-400 flex items-center justify-center">
              <Play className="w-3 h-3 text-white" fill="white" />
            </div>
            <span className="font-semibold">MotionScript</span>
          </div>

        </div>
      </footer>
    </div>
  );
}
