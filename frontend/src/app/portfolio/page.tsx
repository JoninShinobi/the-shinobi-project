'use client';

import React, { useState } from 'react';
import { ArrowLeft, ExternalLink, X, Layers, Shield, Target } from 'lucide-react';
import Link from 'next/link';

const Logo = ({ className = "h-10 w-10" }: { className?: string }) => (
  <svg className={className} viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="512" height="512" rx="80" className="fill-zinc-950" />
    <g transform="translate(256, 256)">
      <path d="M-40 -40 L-140 -40 L-100 -140 L0 -100 Z" className="fill-red-700" />
      <path d="M40 -40 L40 -140 L140 -100 L100 0 Z" className="fill-zinc-300" />
      <path d="M40 40 L140 40 L100 140 L0 100 Z" className="fill-red-700" />
      <path d="M-40 40 L-40 140 L-140 100 L-100 0 Z" className="fill-zinc-300" />
      <rect x="-40" y="-40" width="80" height="80" className="fill-zinc-900" />
      <rect x="-15" y="-15" width="30" height="30" className="fill-red-700" transform="rotate(45)" />
    </g>
  </svg>
);

// Deployment data - tactical terminology
const deployments = [
  {
    id: 'sound-box',
    codename: 'Sound Box',
    classification: 'Digital Application',
    briefing: 'Audio infrastructure engineered for immersive soundscape delivery. A precision tool for auditory engagement and ambient control systems.',
    capabilities: ['React', 'Web Audio API', 'Node.js'],
    status: 'Deployed',
    sector: 'Entertainment',
  },
  {
    id: 'hortus-cognitor',
    codename: 'Hortus Cognitor',
    classification: 'Intelligence Platform',
    briefing: 'Botanical reconnaissance system. Machine learning architecture for plant identification, growth tracking, and cultivation optimization.',
    capabilities: ['Python', 'TensorFlow', 'Django'],
    status: 'Active',
    sector: 'Agriculture',
  },
  {
    id: 'kerry-gallagher',
    codename: 'KG Protocol',
    classification: 'Personal Fortification',
    briefing: 'Individual digital presence. A refined command center for professional identity projection and portfolio deployment.',
    capabilities: ['Next.js', 'Tailwind CSS', 'Vercel'],
    status: 'Deployed',
    sector: 'Creative',
  },
  {
    id: 'community-harvest',
    codename: 'Community Harvest',
    classification: 'Community Infrastructure',
    briefing: 'Local territory coordination platform. Connects operatives through shared resource distribution and sustainable supply chain management.',
    capabilities: ['Django', 'PostgreSQL', 'HTMX'],
    status: 'Active',
    sector: 'Community',
  },
  {
    id: 'the-laurel',
    codename: 'The Laurel',
    classification: 'Business Operations',
    briefing: 'Local business command structure. Integrated booking systems, customer engagement protocols, and operational automation.',
    capabilities: ['React', 'Node.js', 'MongoDB'],
    status: 'Deployed',
    sector: 'Hospitality',
  },
  {
    id: 'what-is-real',
    codename: 'Project Verity',
    classification: 'Experimental Division',
    briefing: 'Digital perception research. An experimental interface exploring the boundaries between virtual construction and user reality.',
    capabilities: ['Three.js', 'WebGL', 'React'],
    status: 'In Development',
    sector: 'Research',
  },
  {
    id: 'haiku-tea',
    codename: 'HaikuTea',
    classification: 'Commerce Engine',
    briefing: 'E-commerce fortification for artisanal goods. Secure transaction infrastructure with refined aesthetic presentation layer.',
    capabilities: ['Shopify', 'Liquid', 'JavaScript'],
    status: 'Deployed',
    sector: 'Retail',
  },
];

const DeploymentCard = ({ deployment, onClick }: { deployment: typeof deployments[0]; onClick: () => void }) => (
  <div
    className="group relative bg-zinc-900 border border-zinc-800 overflow-hidden cursor-pointer hover:border-red-700/50 transition-all duration-300 hover:shadow-lg hover:shadow-red-900/10"
    onClick={onClick}
  >
    {/* Diagonal slash accent */}
    <div className="absolute top-0 right-0 w-24 h-24 overflow-hidden">
      <div className="absolute top-0 right-0 w-32 h-1 bg-gradient-to-l from-red-700 to-transparent transform rotate-45 origin-top-right translate-y-8 -translate-x-4" />
    </div>

    {/* Status indicator */}
    <div className="absolute top-4 right-4 flex items-center gap-2">
      <span className={`w-2 h-2 rounded-full ${
        deployment.status === 'Active' ? 'bg-green-500 animate-pulse' :
        deployment.status === 'Deployed' ? 'bg-red-700' :
        'bg-zinc-500'
      }`} />
      <span className="text-xs uppercase tracking-widest text-zinc-500">{deployment.status}</span>
    </div>

    <div className="p-6 pt-12">
      {/* Classification tag */}
      <div className="mb-4">
        <span className="text-xs uppercase tracking-widest text-red-700 font-medium">{deployment.classification}</span>
      </div>

      {/* Codename */}
      <h3 className="text-xl font-bold text-zinc-200 mb-3 group-hover:text-white transition-colors tracking-tight">
        {deployment.codename}
      </h3>

      {/* Briefing */}
      <p className="text-zinc-500 text-sm mb-6 leading-relaxed line-clamp-3">{deployment.briefing}</p>

      {/* Sector */}
      <div className="flex items-center gap-2 mb-4 pb-4 border-b border-zinc-800">
        <Target size={14} className="text-zinc-600" />
        <span className="text-xs uppercase tracking-widest text-zinc-600">Sector: {deployment.sector}</span>
      </div>

      {/* Capabilities */}
      <div className="flex flex-wrap gap-2">
        {deployment.capabilities.map((cap, index) => (
          <span key={index} className="px-2 py-1 bg-zinc-950 border border-zinc-800 text-zinc-500 text-xs uppercase tracking-wider">
            {cap}
          </span>
        ))}
      </div>
    </div>

    {/* Bottom accent line */}
    <div className="absolute bottom-0 left-0 w-0 h-0.5 bg-red-700 group-hover:w-full transition-all duration-500" />
  </div>
);

const DeploymentModal = ({ deployment, onClose }: { deployment: typeof deployments[0] | null; onClose: () => void }) => {
  if (!deployment) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-sm" onClick={onClose}>
      <div
        className="bg-zinc-900 border border-zinc-800 max-w-2xl w-full max-h-[90vh] overflow-y-auto relative"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header with grid pattern */}
        <div className="relative h-32 bg-zinc-950 border-b border-zinc-800 overflow-hidden">
          {/* Grid pattern background */}
          <div className="absolute inset-0 opacity-10">
            <svg width="100%" height="100%">
              <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#71717a" strokeWidth="0.5"/>
              </pattern>
              <rect width="100%" height="100%" fill="url(#grid)" />
            </svg>
          </div>

          {/* Diagonal accent */}
          <div className="absolute -bottom-12 -left-12 w-48 h-48 bg-red-900/20 transform -skew-x-12" />

          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-2 bg-zinc-800/50 hover:bg-zinc-800 border border-zinc-700 transition-colors"
          >
            <X className="text-zinc-400 w-4 h-4" />
          </button>

          {/* Header content */}
          <div className="absolute bottom-4 left-6">
            <span className="text-xs uppercase tracking-widest text-red-700 font-medium">{deployment.classification}</span>
            <h2 className="text-2xl font-bold text-white tracking-tight mt-1">{deployment.codename}</h2>
          </div>

          {/* Status badge */}
          <div className="absolute bottom-4 right-6 flex items-center gap-2 px-3 py-1 bg-zinc-900/80 border border-zinc-800">
            <span className={`w-2 h-2 rounded-full ${
              deployment.status === 'Active' ? 'bg-green-500' :
              deployment.status === 'Deployed' ? 'bg-red-700' :
              'bg-zinc-500'
            }`} />
            <span className="text-xs uppercase tracking-widest text-zinc-400">{deployment.status}</span>
          </div>
        </div>

        <div className="p-6">
          {/* Mission Briefing */}
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-3">
              <Shield size={16} className="text-red-700" />
              <h4 className="text-xs uppercase tracking-widest text-zinc-400 font-medium">Mission Briefing</h4>
            </div>
            <p className="text-zinc-400 leading-relaxed">{deployment.briefing}</p>
          </div>

          {/* Operational Details */}
          <div className="grid grid-cols-2 gap-4 mb-8">
            <div className="bg-zinc-950 border border-zinc-800 p-4">
              <span className="text-xs uppercase tracking-widest text-zinc-600 block mb-2">Target Sector</span>
              <span className="text-zinc-200 font-medium">{deployment.sector}</span>
            </div>
            <div className="bg-zinc-950 border border-zinc-800 p-4">
              <span className="text-xs uppercase tracking-widest text-zinc-600 block mb-2">Deployment Status</span>
              <span className="text-zinc-200 font-medium">{deployment.status}</span>
            </div>
          </div>

          {/* Tech Stack / Capabilities */}
          <div className="mb-8">
            <div className="flex items-center gap-2 mb-3">
              <Layers size={16} className="text-red-700" />
              <h4 className="text-xs uppercase tracking-widest text-zinc-400 font-medium">Infrastructure Stack</h4>
            </div>
            <div className="flex flex-wrap gap-2">
              {deployment.capabilities.map((cap, index) => (
                <span key={index} className="px-3 py-2 bg-zinc-950 border border-zinc-800 text-zinc-300 text-sm">
                  {cap}
                </span>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t border-zinc-800">
            <button className="flex-1 py-3 bg-red-700 text-white font-bold uppercase tracking-widest text-sm hover:bg-red-800 transition-colors flex items-center justify-center gap-2">
              <ExternalLink size={16} />
              View Deployment
            </button>
            <button
              onClick={onClose}
              className="px-6 py-3 border border-zinc-700 text-zinc-400 hover:border-zinc-600 hover:text-zinc-300 transition-colors uppercase tracking-widest text-sm"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default function PortfolioPage() {
  const [selectedDeployment, setSelectedDeployment] = useState<typeof deployments[0] | null>(null);
  const [filter, setFilter] = useState<string>('all');

  const sectors = ['all', ...new Set(deployments.map(d => d.sector))];
  const filteredDeployments = filter === 'all' ? deployments : deployments.filter(d => d.sector === filter);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-300 font-sans selection:bg-red-900 selection:text-white">

      {/* Navigation */}
      <nav className="fixed w-full z-40 bg-zinc-950/95 backdrop-blur-md border-b border-zinc-800 py-4">
        <div className="container mx-auto px-6 flex justify-between items-center">
          <Link href="/" className="flex items-center gap-3">
            <Logo className="h-10 w-10" />
            <span className="text-lg font-bold text-white tracking-widest uppercase">The Shinobi Project</span>
          </Link>

          <div className="hidden md:flex items-center gap-8">
            <Link href="/#mission" className="text-xs font-medium hover:text-red-500 transition-colors uppercase tracking-widest">Mission</Link>
            <Link href="/#services" className="text-xs font-medium hover:text-red-500 transition-colors uppercase tracking-widest">Arsenal</Link>
            <Link href="/portfolio" className="text-xs font-medium text-red-500 uppercase tracking-widest">Deployments</Link>
            <button className="px-5 py-2 border border-red-700 text-red-500 hover:bg-red-700 hover:text-white transition-all duration-300 text-xs font-bold uppercase tracking-widest">
              Initiate
            </button>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-16 px-6 border-b border-zinc-800 relative overflow-hidden">
        {/* Background grid */}
        <div className="absolute inset-0 opacity-5">
          <svg width="100%" height="100%">
            <pattern id="heroGrid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#71717a" strokeWidth="0.5"/>
            </pattern>
            <rect width="100%" height="100%" fill="url(#heroGrid)" />
          </svg>
        </div>

        {/* Diagonal accent */}
        <div className="absolute top-0 right-0 w-1/3 h-full bg-gradient-to-l from-red-900/10 to-transparent transform skew-x-12 origin-top-right" />

        <div className="container mx-auto relative z-10">
          <Link href="/" className="inline-flex items-center gap-2 text-zinc-500 hover:text-white transition-colors mb-8 group">
            <ArrowLeft size={14} className="group-hover:-translate-x-1 transition-transform" />
            <span className="text-xs uppercase tracking-widest">Return to Base</span>
          </Link>

          <div className="flex items-center gap-3 mb-4">
            <div className="h-px w-8 bg-red-700" />
            <span className="text-xs uppercase tracking-widest text-red-700 font-medium">Field Operations</span>
          </div>

          <h1 className="text-4xl md:text-5xl font-bold text-white mb-6 tracking-tight">
            Deployment <span className="text-red-700">Registry</span>
          </h1>
          <p className="text-lg text-zinc-400 max-w-2xl leading-relaxed">
            Active and completed operations. Each deployment represents infrastructure built to defend local territory against corporate encroachment.
          </p>
        </div>
      </section>

      {/* Filter */}
      <section className="py-6 px-6 border-b border-zinc-800 bg-zinc-900/50">
        <div className="container mx-auto">
          <div className="flex items-center gap-4">
            <span className="text-xs uppercase tracking-widest text-zinc-600">Filter by Sector:</span>
            <div className="flex flex-wrap gap-2">
              {sectors.map((sector) => (
                <button
                  key={sector}
                  onClick={() => setFilter(sector)}
                  className={`px-3 py-1.5 text-xs uppercase tracking-widest transition-all duration-300 ${
                    filter === sector
                      ? 'bg-red-700 text-white'
                      : 'bg-zinc-900 text-zinc-500 hover:text-zinc-300 border border-zinc-800 hover:border-zinc-700'
                  }`}
                >
                  {sector}
                </button>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Deployments Grid */}
      <section className="py-16 px-6 relative">
        {/* Subtle background pattern */}
        <div className="absolute inset-0 opacity-[0.02]">
          <svg width="100%" height="100%">
            <pattern id="deployGrid" width="60" height="60" patternUnits="userSpaceOnUse">
              <path d="M 60 0 L 0 0 0 60" fill="none" stroke="#fff" strokeWidth="1"/>
            </pattern>
            <rect width="100%" height="100%" fill="url(#deployGrid)" />
          </svg>
        </div>

        <div className="container mx-auto relative z-10">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredDeployments.map((deployment) => (
              <DeploymentCard
                key={deployment.id}
                deployment={deployment}
                onClick={() => setSelectedDeployment(deployment)}
              />
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6 bg-black border-t border-zinc-800 relative overflow-hidden">
        {/* Background accent */}
        <div className="absolute inset-0 flex items-center justify-center opacity-5 pointer-events-none">
          <Logo className="w-96 h-96" />
        </div>

        <div className="container mx-auto text-center relative z-10">
          <div className="flex items-center justify-center gap-3 mb-6">
            <div className="h-px w-12 bg-zinc-700" />
            <span className="text-xs uppercase tracking-widest text-zinc-500">New Operation</span>
            <div className="h-px w-12 bg-zinc-700" />
          </div>

          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6 tracking-tight">Ready to Deploy?</h2>
          <p className="text-zinc-400 mb-8 max-w-lg mx-auto leading-relaxed">
            Your territory awaits fortification. Initiate contact and we will assess your operational requirements.
          </p>
          <Link href="/#contact">
            <button className="px-8 py-4 bg-red-700 text-white font-bold uppercase tracking-widest text-sm hover:bg-red-800 transition-colors">
              Initiate Protocol
            </button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-black py-8 px-6 border-t border-zinc-800">
        <div className="container mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-center text-xs text-zinc-600 uppercase tracking-widest">
            <p>&copy; {new Date().getFullYear()} The Shinobi Project</p>
            <p>Forged in the Shadows</p>
          </div>
        </div>
      </footer>

      {/* Modal */}
      <DeploymentModal deployment={selectedDeployment} onClose={() => setSelectedDeployment(null)} />
    </div>
  );
}
